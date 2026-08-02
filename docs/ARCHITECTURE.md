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
| Persistance | JSONL poussé vers un jeu de données Hugging Face | Aucune base en v1 ; une clé absente ne doit jamais casser une exécution |

**Sur l'absence de cadriciel** : les offres d'emploi citent LangChain. Le compromis est assumé — un candidat qui a écrit sa boucle explique mieux ses choix qu'un candidat qui a assemblé des briques. LangChain pourra être ajouté ensuite pour la couverture.

**Sur le SDK Docker plutôt que le SDK Gradio** : le SDK Gradio masque le
conteneur, le build et l'API. Or c'est précisément ce que les offres d'AI
engineer citent — Docker, CI/CD, déploiement d'API. Gradio reste le cadre
d'interface *dans* le conteneur : on ne perd rien et on gagne la portabilité
vers Render si le palier gratuit se révèle insuffisant.

**Sur la persistance — Supabase est écarté de la v1.** Il figurait dans la
première pile par familiarité, pas par besoin. Les traces sont des lignes JSONL
poussées vers un jeu de données Hugging Face : aucune base, aucune clé, aucune
latence, un mode de panne en moins. Le palier gratuit de Supabase met par
ailleurs un projet inactif en pause au bout d'une semaine, et une démonstration
publique dont la base tombe en veille est une démonstration morte.

La variable `ARPENT_STORE` reste la couture par laquelle une base entrerait si
le projet 2 en révélait le besoin. Tant que ce besoin n'existe pas, il n'y a
rien à installer.

**Isolation du fournisseur de modèle** : tous les appels passent par une interface unique. Le projet 2 doit pouvoir brancher un second fournisseur sans réécriture, pour la comparaison chiffrée.

## 6. Maîtrise du coût

Trois leviers, prévus dès la conception et non ajoutés après coup :

- **Routage** — planification sur Haiku, **validation d'instrument et synthèse
  sur Sonnet**. Le validateur ne descend pas sur le modèle économique : c'est
  l'étape qui porte la valeur du projet, et l'écart de coût est de quelques
  centimes par exécution. Les trois sont pilotés par variables
  d'environnement, ce qui fait de l'écart Haiku/Sonnet sur le validateur un
  cas de mesure prêt à l'emploi pour le projet 2
- **Cache d'invite** — une lecture en cache coûte 10 % du prix d'entrée, mais
  une écriture en coûte 125 % (durée 5 min) ou 200 % (durée 1 h). Le cache
  n'est donc rentable qu'à partir de la deuxième lecture. **Deux pièges
  vérifiés** : le préfixe minimal cachable est de 1 024 jetons sur Sonnet 5
  mais de **4 096 sur Haiku 4.5** — une invite plus courte n'est pas mise en
  cache, *sans erreur ni avertissement* ; et la durée par défaut est de
  5 minutes, ce qui ne survit pas entre deux visites espacées d'une démo
  publique. Le cache sert donc **à l'intérieur d'une exécution** (le
  validateur est appelé deux fois) et **pendant les rejeux du projet 2**, pas
  entre visiteurs
- **Traitement par lots** — 50 % de réduction, applicable aux évaluations du projet 2 qui ne sont jamais urgentes
- **Comptage avant envoi** — l'endpoint de comptage de jetons est **gratuit**
  et soumis à des limites de débit distinctes de celles de la génération. Le
  plafond par exécution s'applique donc **avant** de payer, pas après avoir
  constaté le dépassement

Ces leviers sont eux-mêmes un objet de démonstration : savoir qu'une évaluation se lance en lot, ou qu'un cache mal dimensionné coûte 25 % de plus au lieu d'économiser 90 %, est un signal de praticien.

**Ce qui conditionne réellement la facture**, par ordre d'effet mesuré :

| Facteur | Effet | Levier |
|---|---|---|
| Taille de la charge utile envoyée au modèle | dominant | Projection de champs à la collecte : le modèle ne voit que nom, description tronquée, mots-clés, dates |
| Taille de l'échantillon soumis au validateur | fort | 10 éléments suffisent à détecter une dérive ; 40 ne détectent pas quatre fois mieux |
| Nombre de replanifications | ×1 à ×3 sur tout ce qui précède | Plafond à 2, déjà posé |
| Invites système | fixe par appel | Cachables seulement au-delà du seuil du modèle |
| Verbosité demandée en sortie | modéré | Référencer les paquets par indice plutôt que les redécrire |

La règle qui les résume : **la frontière déterministe/modèle est aussi une
frontière de coût.** Tout ce que la couche déterministe garde pour elle n'est
jamais facturé.

## 7. Ce que l'architecture prépare pour le projet 2

- Chaque exécution enregistre sa trace complète : plan, sources, validations, replanifications, verdict
- Le verdict est structuré, donc comparable automatiquement
- L'interface fournisseur permet de rejouer les mêmes cas sur deux modèles
- Une variante multi-agent sera implémentée **uniquement pour être mesurée** et démontrée inférieure

**Cas de mesure déjà identifiés**, dans l'ordre d'intérêt :

1. **Un modèle économique contre Sonnet 5 sur le validateur.** Gemini 2.5
   Flash-Lite est à 0,10 $/0,40 $ par million de jetons contre 3 $/15 $ pour
   Sonnet 5 — un facteur 30. La question est de savoir si le jugement de
   pertinence sémantique tient à ce prix. Les mesures publiées sur les sorties
   structurées montrent que la conformité au schéma est élevée sur les modèles
   ouverts, mais que **l'exactitude des valeurs décroche** : c'est précisément
   la dimension que le validateur exerce. Les deux issues sont exploitables —
   s'il tient, c'est un résultat publiable ; s'il ne tient pas, la mesure
   justifie l'architecture.
2. Haiku 4.5 contre Sonnet 5 sur le validateur — même question, écart plus
   faible, à l'intérieur d'une même famille de modèles.
3. La variante multi-agent contre l'agent unique.

Les trois sont accessibles sans écrire de code supplémentaire : le routage est
piloté par variables d'environnement et tous les appels passent par
l'interface fournisseur.

**Note d'usage** : les paliers gratuits d'API n'ont pas leur place sur le
chemin public — le plafond de Groq à 12 000 jetons par minute est inférieur à
ce qu'une seule exécution consomme en entrée. Ils ont en revanche leur place
dans les rejeux du projet 2, où la latence est indifférente et où le volume
fait mordre l'écart de prix.

## 8. Ce qui est explicitement écarté

| Écarté | Motif |
|---|---|
| Agents pairs communicants | Dégradation mesurée de 39 à 70 % |
| Instruction système partagée entre orchestrateur et sous-agent | Confond les rôles, fait payer le coût de l'orchestrateur à chaque appel |
| Modèle pour les calculs | Moins fiable et plus cher qu'une fonction |
| Base vectorielle en v1 | Aucun besoin de recherche sémantique sur ce périmètre |
