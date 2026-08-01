# DELIVERY — Arpent

Version 2 · statut : semaine 1 — squelette en place, boucle d'agent non écrite.

---

## 1. Comment la solution atteint son usager

**Une URL publique. Rien à installer, aucun compte.**

C'est un critère de preuve, pas un confort : un dépôt clonable ne démontre rien à un recruteur qui dispose de cinq minutes. Le produit doit être joignable et fonctionner sans préalable.

| Canal | Rôle |
|---|---|
| URL publique (Hugging Face Spaces) | Accès principal, palier gratuit |
| Dépôt public | Lecture du code, documentation |
| Serveur MCP (v3) | Accès par d'autres agents |

## 2. Chaîne de déploiement

Pousser sur la branche principale déclenche le déploiement. Le palier gratuit de la plateforme d'hébergement suffit au volume prévu.

**Barrières avant fusion :**

1. Les tests unitaires passent
2. La suite d'évaluation ne régresse pas — seuil de qualité minimal
3. Aucune clé en clair dans le différentiel

La deuxième barrière est le point important : **une régression de qualité bloque au même titre qu'un test rouge**. C'est ce qui distingue un projet évalué d'un projet simplement testé.

## 3. Suivi en production

| Indicateur | Seuil d'alerte |
|---|---|
| Taux d'exécutions abouties | < 90 % |
| Latence médiane | > 120 s |
| Taux de replanification | > 40 % — l'instrument dérive |
| Coût moyen par exécution | > 0,20 $ |
| Consommation mensuelle | 50 % puis 80 % du budget |

Le taux de replanification est le plus instructif : il mesure la dérive des sources amont. Une hausse brutale signifie qu'une API a changé son comportement.

## 4. Maintenance

**Charge estimée : 1 à 2 h par mois** après la mise en service.

| Fréquence | Tâche |
|---|---|
| Mensuel | Vérifier les alertes, consulter le tableau d'évaluation |
| Trimestriel | Rejouer la suite complète, mettre à jour les dépendances |
| Sur événement | Réagir à une rupture d'API amont |

Cette charge doit rester compatible avec un budget global de 10 h/semaine partagé entre trois projets.

## 5. Calendrier — 12 semaines

Trois écarts par rapport à la première version de ce document, chacun motivé.

**Le déploiement passe de la fin à la mi-parcours.** Le critère éliminatoire —
joignable — devient acquis par construction plutôt que constaté trop tard pour
réagir. L'ancien calendrier gardait le risque principal pour la fin, ce que ce
document dénonce partout ailleurs.

**Le temps d'apprentissage est compté.** Python, `uv`, `pytest`, Pydantic,
Docker et Gradio sont six outils inconnus. La règle posée dès l'origine — le
temps d'apprentissage compte dans le délai — impose de le budgéter, pas de
l'espérer. D'où 12 semaines et non 10.

**La diffusion devient une piste continue** à 1 h par semaine à partir de la
semaine 5, prélevée sur les dix. Neuf semaines de construction suivies d'une
semaine de diffusion est le schéma d'échec classique.

| S | Constr. | Appr. | Diff. | Livrable |
|---|---|---|---|---|
| 1 | 6 h | 4 h | — | Comptes, dépôt, licence, Python 3.12, `uv`, `ruff`, `pytest`, CI verte |
| 2 | 6 h | 4 h | — | Pydantic, HTTP, premier appel modèle, trace JSONL, coût affiché |
| 3 | 8 h | 2 h | — | Interface fournisseur, routage par variables d'environnement |
| 4 | 9 h | 1 h | — | Connecteur npm, les trois règles de `DATA.md` §5 testées |
| 5 | 8 h | 1 h | 1 h | **Boucle complète, npm seul, en CLI** + première note publique |
| 6 | 9 h | — | 1 h | **URL PUBLIQUE** — Docker, Space, UI minimale ⟵ *point de contrôle* |
| 7 | 9 h | — | 1 h | Validation d'instrument et replanification, étapes en direct |
| 8 | 9 h | — | 1 h | Connecteur GitHub, dégradation gracieuse testée |
| 9 | 9 h | — | 1 h | Mesures, seuils, confiance — calibrage sur 12-15 cas |
| 10 | 9 h | — | 1 h | Interface conforme au §3 de `DESIGN.md`, accessibilité AA |
| 11 | 9 h | — | 1 h | Robustesse, plafonds, moins de 100 s mesuré, README |
| 12 | 4 h | — | 6 h | Diffusion concentrée, journal des usages, rétrospective |

**Total : 120 h — 95 h de construction, 12 h d'apprentissage, 13 h de diffusion.**

**Point de contrôle en semaine 6, ferme.** Si l'URL publique ne répond pas,
l'ordre de réduction s'applique immédiatement, sans attendre un dérapage
supplémentaire : Supabase, puis le connecteur GitHub, puis les replanifications
ramenées à une, puis la route d'API.

**Jamais coupés** : l'URL publique, la validation d'instrument, la section
« ce qui n'a pas pu être mesuré », la piste de diffusion.

Règle générale : **une v1 étroite qui existe bat une v1 ambitieuse qui n'existe pas.**

## 6. Enchaînement des projets

| Projet | Dépendance | Durée |
|---|---|---|
| 1 — agent d'analyse | — | 12 semaines |
| 2 — suite d'évaluation | Traces produites par le projet 1 | 4-5 semaines |
| 3 — serveur MCP | Projet 1 fonctionnel | 3-4 semaines |

**Priorité en cas de glissement** : sacrifier le projet 3, jamais le projet 2. La suite d'évaluation est le différenciateur — presque aucun portefeuille n'en contient, et les offres d'emploi citent explicitement la fiabilité en production.

## 7. Critères de succès du projet 1

| Critère | Vérification |
|---|---|
| Joignable | Une URL publique répond |
| Rapide | Verdict en moins de 2 minutes |
| Honnête | Confiance et angles morts sur chaque verdict |
| Robuste | Une source indisponible ne casse pas l'exécution |
| Employé | Au moins un usage documenté par un tiers |

**Critère d'abandon** : rien de joignable après 12 semaines, alors qu'un périmètre réduit était possible.

## 8. Décisions arrêtées

- **Nom** — `arpent`, partout : dépôt, paquet Python, Space, dossier local.
  Vérifié disponible sur npm. Organisation GitHub : Gooma Lab.
- **Licence** — MIT. Aucun enjeu commercial en v1, et c'est ce qui maximise la
  lecture et la réutilisation du code, qui sont sa raison d'être.
- **Hébergement de repli** — Render, seul PaaS conservant un vrai palier
  gratuit permanent. Le SDK Docker de Hugging Face rend la bascule sans
  réécriture : c'est le même conteneur. Réserve à connaître : Render descend
  après 15 minutes d'inactivité, contre 48 heures pour Hugging Face.
- **Interpréteur** — Python 3.12 en local et en conteneur. Une divergence entre
  l'interpréteur de développement et celui du déploiement est détectée par un
  test, pas au déploiement.

## 9. Décision reportée à la semaine 6 — le démarrage à froid

Le palier gratuit `cpu-basic` s'endort après 48 h d'inactivité et ne permet pas
de configurer ce délai. La question n'est pas de savoir s'il faut maintenir le
Space éveillé, mais **sur quel nombre trancher**. Elle est donc reportée à la
semaine 6, où le nombre existera.

**Ce qui est déjà chiffré.**

| Élément | Valeur |
|---|---|
| Compute transféré à l'hébergeur si l'on maintient éveillé | ≈ 585 h/mois, soit **≈ 4,40 $/mois** — au prorata des vCPU depuis `cpu-upgrade` à 0,03 $/h ; **inférence, pas un tarif publié** |
| Coût de l'appel programmé lui-même | 0 $ — GitHub Actions est illimité sur les dépôts publics |
| Règle publiée par Hugging Face sur les appels de maintien | aucune |
| Incident documenté de mise en pause pour abus (mai 2026) | à **720 appels/jour**. Un appel toutes les 36 h en fait 0,67 — un rapport de 1 000, hors de portée d'une règle de débit |

**Ce qui ne l'est pas, et qui décide.** La durée réelle du réveil. Elle a été
annoncée « 30 à 60 s » sans avoir été mesurée : c'est une estimation, et elle
n'a pas sa place dans un projet dont la thèse est qu'on n'affiche pas un
chiffre qu'on ne peut pas reconstituer.

Ce qui est certain, en revanche, c'est **la probabilité de subir ce réveil**.
Le persona P2 arrive seul, à froid, plusieurs jours après la dernière visite —
c'est la définition même du visiteur qui le paie. Ce n'est pas un cas rare,
c'est le cas nominal.

**Protocole en semaine 6.** Mesurer le réveil, inscrire la valeur ici, puis :

- **sous ~20 s** — ne rien faire, l'annoncer en une ligne dans le README. Un
  produit dont la valeur est d'afficher ses limites peut afficher celle-là.
- **au-delà de ~45 s** — l'appel toutes les 36 h devient défendable : 4,40 $/mois
  de compute transféré, exposition négligeable à cette fréquence.

**Levier à privilégier dans les deux cas** : réduire la durée du réveil plutôt
que l'éviter — image Docker minimale, dépendances élaguées, aucun
téléchargement au démarrage. C'est mesurable, entièrement sous notre contrôle,
et sans aucune question de conditions d'utilisation.

| Date | Réveil mesuré | Décision |
|---|---|---|
| — | *non mesuré* | *reportée à la semaine 6* |
