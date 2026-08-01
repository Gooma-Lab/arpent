# ARCHITECTURE — Arpent

Version 2 · statut : semaine 1 — squelette en place, boucle d'agent non écrite.

---

## 1. Principe directeur

**Un agent unique détient le contexte et engendre des sous-agents éphémères.**

Chaque sous-agent s'exécute dans un contexte neuf, avec sa propre instruction système, accomplit une tâche isolée et rend un unique résumé. Aucun canal entre pairs, aucun état mutable partagé.

Ce n'est pas un choix esthétique, c'est le seul motif multi-agent qui a survécu à la mise en production. Justification chiffrée : une recherche Google, citée en mars 2026, mesure une **dégradation de 39 à 70 % des performances sur les tâches de raisonnement séquentiel** pour les architectures multi-agents comparées à un agent unique ; les taux d'échec en production sont rapportés entre 41 et 87 %.

La cause n'est pas le modèle : **les résumés perdent les décisions implicites**. Un agent informé qu'« une approche événementielle a été retenue » ignore quels schémas ont été choisis, quels modes de défaillance ont été écartés. Seul le partage de trace complète fonctionne, et il sature le contexte.

**Test avant tout découpage** : non pas « ces sous-tâches sont-elles parallélisables ? » mais « connaître le résultat de A changerait-il ma façon d'aborder B ? ». Si oui, pas de découpage.

## 2. Frontière déterministe / modèle

C'est la décision d'architecture la plus importante du projet. Un modèle de langage ne doit jamais faire ce qu'un compteur fait mieux.

| Étape | Nature | Justification |
|---|---|---|
| Récupération des sources | **Déterministe** | Appels HTTP, pagination, limites de débit |
| Comptage, agrégats, médianes | **Déterministe** | Arithmétique — un modèle y est moins fiable et plus cher |
| Application des seuils | **Déterministe** | Règles figées avant exécution |
| Décomposition de la demande | **Modèle** | Planification sous ambiguïté |
| Validation d'instrument | **Modèle** | Jugement de pertinence sémantique |
| Synthèse et verdict | **Modèle** | Arbitrage entre signaux contradictoires |

**Sans les trois lignes « modèle », ce projet n'est qu'un script.** C'est là qu'est la valeur d'ingénierie.

## 3. La boucle

```
Demande en langage naturel
        │
        ▼
[1] PLANIFIER            (modèle) ── sélection des sources, termes, filtres
        │
        ▼
[2] COLLECTER            (déterministe) ── npm, GitHub — parallélisable
        │
        ▼
[3] VALIDER L'INSTRUMENT (sous-agent éphémère)
        │                 « l'échantillon correspond-il à la demande ? »
        │
        ├── NON ──► retour en [1] avec le diagnostic  (max 2 replanifications)
        │
        └── OUI ──▼
[4] MESURER              (déterministe) ── indicateurs, seuils
        │
        ▼
[5] SYNTHÉTISER          (modèle) ── verdict + confiance + angles morts
```

**L'étape 3 est le cœur du projet.** Elle est née d'un échec réel : une requête portant sur les wikis remontait des extracteurs de réseaux sociaux, parce que la recherche portait aussi sur les descriptions. Le défaut était détectable en dix secondes — il suffisait de regarder un échantillon.

L'agent fait donc systématiquement ce contrôle, et **replanifie s'il constate une dérive**. C'est de l'auto-évaluation, et c'est ce qui distingue ce projet d'un extracteur.

Garde-fou : deux replanifications au maximum. Au-delà, le verdict est rendu avec une confiance dégradée et le motif explicite.

## 4. Sources enfichables — deux rôles, pas un contrat unique

npm et GitHub ne font pas le même travail. On ne cherche jamais sur GitHub :
on résout le champ `repository` d'un paquet déjà trouvé sur npm. npm
**découvre**, GitHub **enrichit**. Leur donner la même signature reviendrait à
combattre sa propre abstraction dès le premier connecteur.

Socle commun aux deux rôles :

```
capacités()      → ce que la source sait mesurer
limites()        → ce que la source ne peut PAS mesurer
```

Source de découverte — on lui pose une question :

```
collecter(plan)  → données brutes + métadonnées de collecte
échantillon(n)   → n éléments lisibles, pour la validation d'instrument
```

Source d'enrichissement — on lui présente ce qu'on a déjà trouvé :

```
enrichir(éléments) → les mêmes éléments, augmentés + métadonnées de collecte
```

La méthode `limites()` n'est pas décorative : elle alimente directement la section « angles morts » du verdict. Une source qui ne connaît pas le signal d'argent le déclare, et le verdict en tient compte.

Une source d'enrichissement est **toujours facultative par construction** : si
elle échoue, le verdict est rendu sans elle, la confiance baisse, et son
absence est nommée. Une source de découverte qui échoue arrête l'exécution —
il n'y a plus rien à mesurer.

Correspondance avec les identifiants du code : voir `GLOSSARY.md` §1.

**Sources v1** : registre npm (public, sans clé), API GitHub (clé gratuite, 5 000 requêtes/heure).
**Source v2** : France Travail (API publique) — apporte le signal d'argent absent de la v1.

Ajouter une source ne modifie que son connecteur. C'est ce qui permet à la v2 d'exister sans refonte.

## 5. Pile technique

| Couche | Choix | Motif |
|---|---|---|
| Langage | Python | Coût d'entrée de la spécialisation, payé ici |
| Modèle | Claude Sonnet 5 | Cohérence avec le projet 3 (MCP) |
| Orchestration | SDK brut, pas de cadriciel | Écrire sa boucle fait mieux comprendre que l'assembler |
| Hébergement | Hugging Face Spaces, **SDK Docker** | Gratuit, URL publique, canal reconnu — et le `Dockerfile` reste visible dans le dépôt |
| Persistance | JSONL local, Supabase **optionnel** | Une clé absente ne doit jamais casser une exécution |

**Sur l'absence de cadriciel** : les offres d'emploi citent LangChain. Le compromis est assumé — un candidat qui a écrit sa boucle explique mieux ses choix qu'un candidat qui a assemblé des briques. LangChain pourra être ajouté ensuite pour la couverture.

**Sur le SDK Docker plutôt que le SDK Gradio** : le SDK Gradio masque le
conteneur, le build et l'API. Or c'est précisément ce que les offres d'AI
engineer citent — Docker, CI/CD, déploiement d'API. Gradio reste le cadre
d'interface *dans* le conteneur : on ne perd rien et on gagne la portabilité
vers Render si le palier gratuit se révèle insuffisant.

**Sur la persistance** : le produit doit fonctionner sans base. Les traces
partent en JSONL, poussées vers un jeu de données Hugging Face ; Supabase
s'active par variable d'environnement. Une démonstration publique dont la base
tombe en veille est une démonstration morte.

**Isolation du fournisseur de modèle** : tous les appels passent par une interface unique. Le projet 2 doit pouvoir brancher un second fournisseur sans réécriture, pour la comparaison chiffrée.

## 6. Maîtrise du coût

Trois leviers, prévus dès la conception et non ajoutés après coup :

- **Routage** — planification sur Haiku, **validation d'instrument et synthèse
  sur Sonnet**. Le validateur ne descend pas sur le modèle économique : c'est
  l'étape qui porte la valeur du projet, et l'écart de coût est de quelques
  centimes par exécution. Les trois sont pilotés par variables
  d'environnement, ce qui fait de l'écart Haiku/Sonnet sur le validateur un
  cas de mesure prêt à l'emploi pour le projet 2
- **Cache d'invite** — les lectures en cache coûtent 10 % du prix d'entrée
- **Traitement par lots** — 50 % de réduction, applicable aux évaluations du projet 2 qui ne sont jamais urgentes

Ces trois leviers sont eux-mêmes un objet de démonstration : savoir qu'une évaluation se lance en lot est un signal de praticien.

## 7. Ce que l'architecture prépare pour le projet 2

- Chaque exécution enregistre sa trace complète : plan, sources, validations, replanifications, verdict
- Le verdict est structuré, donc comparable automatiquement
- L'interface fournisseur permet de rejouer les mêmes cas sur deux modèles
- Une variante multi-agent sera implémentée **uniquement pour être mesurée** et démontrée inférieure

## 8. Ce qui est explicitement écarté

| Écarté | Motif |
|---|---|
| Agents pairs communicants | Dégradation mesurée de 39 à 70 % |
| Instruction système partagée entre orchestrateur et sous-agent | Confond les rôles, fait payer le coût de l'orchestrateur à chaque appel |
| Modèle pour les calculs | Moins fiable et plus cher qu'une fonction |
| Base vectorielle en v1 | Aucun besoin de recherche sémantique sur ce périmètre |
