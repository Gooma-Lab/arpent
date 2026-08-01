# GLOSSARY — Arpent

Les documents de `docs/` sont en français ; le code est en anglais (décision D2).

Ce fichier existe pour une raison précise : sur deux points seulement, un terme
français des documents désigne **exactement** un identifiant du code. Partout
ailleurs les documents sont de la prose et ne se traduisent pas. Si l'un des
deux tableaux ci-dessous devient faux, c'est le code ou le document qui a
dérivé — pas ce glossaire.

---

## 1. Contrat de source

`ARCHITECTURE.md` §4 décrit un contrat commun à quatre méthodes. La décision D7
l'a scindé en **deux rôles**, parce que npm et GitHub ne font pas le même
travail : npm **découvre** (on lui pose une question), GitHub **enrichit** (on
lui présente un dépôt déjà trouvé).

| Document (FR) | Code (EN) | Rôle | Implémentation v1 |
|---|---|---|---|
| `capacités()` | `capabilities()` | les deux | — |
| `collecter(plan)` | `collect(plan)` | `DiscoverySource` | `sources/npm.py` |
| `échantillon(n)` | `sample(n)` | `DiscoverySource` | `sources/npm.py` |
| `limites()` | `limits()` | les deux | — |
| — | `enrich(packages)` | `EnrichmentSource` | `sources/github.py` |

`limits()` n'est pas décorative : sa sortie alimente directement la section
« ce qui n'a pas pu être mesuré » du verdict. Une source qui ignore le signal
d'argent le déclare, et le verdict en tient compte.

---

## 2. Les trois verdicts

`DESIGN.md` §4. Le type est fermé — trois valeurs, rien d'autre n'est accepté
(`SECURITY.md` §2).

| Document (FR) | Code (EN) | Signification |
|---|---|---|
| `OCCUPÉ` | `OCCUPIED` | Acteurs actifs et maintenus |
| `OUVERT` | `OPEN` | Peu d'acteurs, ou acteurs abandonnés |
| `DÉSERT` | `DESERT` | Presque rien, et rien n'a jamais pris |

L'interface affiche les formes françaises. Le code, les traces et les cas
d'évaluation n'emploient que les formes anglaises — c'est ce qui rend les
traces comparables automatiquement par le projet 2.

---

## 3. Étapes de la boucle

`ARCHITECTURE.md` §3.

| Document (FR) | Module | Nature |
|---|---|---|
| PLANIFIER | `agent/planner.py` | modèle |
| COLLECTER | `sources/` | déterministe |
| VALIDER L'INSTRUMENT | `agent/validator.py` | modèle |
| MESURER | `measure/` | déterministe |
| SYNTHÉTISER | `agent/synthesizer.py` | modèle |

---

## 4. Termes de mesure

Employés dans `THRESHOLDS.md` et dans `measure/thresholds.py`. Ils n'ont pas
d'équivalent français dans les documents : ils sont nés avec le code.

| Terme | Définition |
|---|---|
| `active` | dernière publication npm < 12 mois **et** dépôt non archivé |
| `maintained` | dernier commit < 6 mois |
| `adopted` | ≥ 500 téléchargements hebdomadaires |
| `announced` / `retrieved` | total annoncé par une API / nombre réellement récupéré (`DATA.md` §5, règle 3) |
| `blind spot` | « angle mort » — ce qui n'a pas pu être mesuré |
| `instrument validation` | « validation d'instrument » — étape 3 de la boucle |
