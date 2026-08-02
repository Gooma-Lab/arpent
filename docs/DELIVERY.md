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
| 2 | 6 h | 4 h | — | Pydantic, HTTP, premier appel modèle, trace JSONL, **comptabilité de jetons par étape** (entrée, sortie, écritures et lectures de cache, coût) — voir §10 |
| 3 | 8 h | 2 h | — | Interface fournisseur, routage par variables d'environnement |
| 4 | 9 h | 1 h | — | Connecteur npm, les trois règles de `DATA.md` §5 testées, **enregistrement/rejeu des réponses d'API** — voir §11 |
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
supplémentaire : le connecteur GitHub d'abord (v1 sur npm seul, limite affichée
dans l'interface), puis les replanifications ramenées à une, puis la route
d'API.

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

## 12. Décision reportée à la semaine 9 — le validateur mérite-t-il Sonnet 5 ?

Le validateur pèse environ 40 % de la facture de jetons. Sa nécessité est
établie — la sonde du 2 août montre trois intrus sur huit résultats pour la
requête `wiki`, capables d'inverser une mesure de distribution. Ce qui n'est
**pas** établi, c'est la **fréquence** de cette contamination. Quatre requêtes
ne mesurent pas un taux.

Le taux de replanification observé sur le jeu de cas de référence le donnera.
Règle écrite d'avance, pour qu'elle ne soit pas négociée après coup :

| Taux de replanification | Lecture | Décision |
|---|---|---|
| **< 10 %** | La dérive est rare sur npm ; Sonnet 5 n'est pas justifié à ce poste | Basculer le validateur sur Haiku 4.5, **ou** passer d'un contrôle systématique à un contrôle échantillonné |
| **10 à 25 %** | Zone d'indécision | Conserver, et remesurer au prochain élargissement de sources |
| **> 25 %** | La contamination est fréquente | Conserver Sonnet 5 ; la sonde était généralisable |
| **> 40 %** | Seuil d'alerte de §3 — l'instrument dérive en amont | Enquêter sur la source, pas sur le modèle |

**Ce que cette décision ne remet pas en cause** : l'existence de l'étape. Le
validateur produit aussi l'échantillon vérifiable et la pénalité de confiance,
qui restent dus quel que soit le taux. La mesure tranche **le coût** — quel
modèle, systématique ou échantillonné — jamais la présence du contrôle. Sans
cette précision, la règle deviendrait une porte de sortie pour supprimer ce
qui coûte.

## 10. Budget de jetons — à mesurer, pas à supposer

Les plafonds de conception (60 k jetons en entrée, 8 k en sortie par exécution)
dérivent d'une estimation écrite **avant** tout code : ≈ 32 k en entrée et 6 k
en sortie pour une analyse de niche. Cette estimation n'a jamais été validée.

C'est le même défaut que celui qui a produit les deux mesures fausses à
l'origine du projet — une valeur reprise sans avoir regardé l'instrument. Elle
est donc traitée comme une hypothèse, pas comme une donnée.

**Ce que la semaine 2 doit produire.** Chaque appel au modèle enregistre dans
la trace : l'étape, le modèle, les jetons d'entrée, de sortie, d'écriture de
cache et de lecture de cache, et le coût. Une commande `arpent cost` restitue
la ventilation par étape.

**Ce que la semaine 11 doit produire.** Ce tableau, rempli — avant et après
optimisation — et repris dans le README. Une ventilation mesurée du budget de
jetons d'un agent est un artefact rare ; c'est aussi la seule façon honnête de
parler d'optimisation.

| Étape | Modèle | Entrée | Sortie | Part du coût |
|---|---|---|---|---|
| PLANIFIER | Haiku 4.5 | — | — | — |
| VALIDER | Sonnet 5 | — | — | — |
| SYNTHÉTISER | Sonnet 5 | — | — | — |

**Point de vigilance vérifié** : le préfixe minimal cachable est de 4 096
jetons sur Haiku 4.5. Une invite système plus courte n'est pas mise en cache et
l'API ne signale rien — il faut lire `cache_creation_input_tokens` et
`cache_read_input_tokens` dans la réponse pour le constater. La comptabilité de
la semaine 2 doit donc enregistrer ces deux champs, faute de quoi on croira
utiliser un cache inexistant.

## 11. Budget financier — le levier est le nombre d'exécutions

La première estimation, 30 à 50 $, reposait sur ~250 exécutions réelles.
**C'est cette hypothèse qui était mauvaise, pas le choix du modèle.** Changer
de fournisseur ferait économiser environ 12 $ au prix de la cohérence avec le
projet 3 et du sujet même du projet 2 ; réduire le nombre d'appels vivants fait
économiser davantage sans rien coûter.

| Période | Exécutions réelles | Pourquoi si peu |
|---|---|---|
| S1-S4 | ~20 | Le connecteur npm se teste sur fixtures, pas sur le réseau |
| S5 — la boucle | ~30 | Le seul bloc qui exige des appels vivants |
| S6-S8 | ~15 | Déploiement, interface et connecteur GitHub rejouent des réponses stockées |
| S9 — calibrage | ~20 | **Les seuils sont déterministes** : un échantillon validé par cas suffit, on rejoue ensuite les seuils sur les données stockées gratuitement |
| S10-S12 | ~30 | Diffusion et usage réel |
| **Total** | **~115** | **≈ 15 $ à 0,13 $ l'exécution** |

**Règle d'enregistrement/rejeu, à mettre en place dès la semaine 4.** Toute
réponse d'API — npm, GitHub, modèle — est enregistrable et rejouable depuis le
disque. Le développement tourne sur les enregistrements ; les appels vivants
sont réservés à ce qui les exige.

Ce n'est pas une économie de bout de chandelle, c'est le mécanisme dont la
suite d'évaluation du projet 2 a besoin de toute façon. Il est simplement
construit plus tôt.

**Échelle de repli**, si la mesure de la semaine 2 donne un coût par exécution
supérieur à l'estimation :

1. Validateur sur Haiku 4.5 **pendant le développement uniquement** — la
   configuration déployée et la ligne de référence des évaluations restent sur
   Sonnet 5. L'artefact public tourne sur la bonne configuration.
2. Réduire l'échantillon soumis au validateur de 40 à 10 éléments.
3. Réduire le nombre de cas de calibrage de 15 à 10.

**Ce qui n'est jamais sacrifié au budget** : le validateur de la configuration
déployée. C'est l'étape qui porte la valeur du projet ; l'économiser reviendrait
à supprimer ce qu'on cherche à démontrer.
