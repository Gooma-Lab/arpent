# THRESHOLDS — Arpent

Version 1 · **valeurs non calibrées** — hypothèses de départ, à confronter au
jeu de cas de référence en semaine 9.

---

## 1. Pourquoi ce document existe

`ARCHITECTURE.md` §2 pose que l'application des seuils est déterministe, avec
des « règles figées avant exécution ». `DESIGN.md` §4 donne la signification
des trois verdicts, jamais leurs valeurs. Sans les chiffres, le verdict est
arbitraire — et c'est la décision produit la plus structurante du projet.

Ce fichier porte les chiffres. Il est **versionné à chaque calibrage** : toute
modification s'inscrit au journal du §5, avec le cas qui l'a provoquée. Un
seuil qu'on déplace sans dire pourquoi est un seuil qu'on ajuste jusqu'à
obtenir le verdict qui plaît.

---

## 2. Définitions élémentaires

Trois prédicats déterministes, appliqués paquet par paquet.

| Prédicat | Règle | Source |
|---|---|---|
| `active` | dernière publication npm < 12 mois **et** dépôt non archivé | npm + GitHub |
| `maintained` | dernier commit < 6 mois | GitHub |
| `adopted` | ≥ 500 téléchargements hebdomadaires | npm |

**Sans GitHub**, `maintained` est indéterminé et `active` se replie sur la
seule date de publication npm. Le verdict reste rendu, la confiance baisse de
25, et la source manquante est nommée (`DESIGN.md` §6).

---

## 3. Règles de verdict

Appliquées à l'échantillon **validé** — jamais aux résultats bruts de la
recherche.

| Verdict | Règle |
|---|---|
| **DESERT** | < 3 paquets pertinents **et** maximum de téléchargements < 200 |
| **OCCUPIED** | ≥ 2 paquets à la fois `maintained` **et** `adopted` |
| **OPEN** | tout le reste — des paquets existent mais sont abandonnés ou non adoptés |

L'ordre d'évaluation est celui du tableau : DESERT d'abord, puis OCCUPIED, et
OPEN par défaut. OPEN est délibérément le cas résiduel — c'est le verdict qui
demande de creuser, donc celui qu'on ne doit jamais prononcer par
enthousiasme.

**Le verdict DESERT s'accompagne toujours de la question qui le tranche** :
quelqu'un paie-t-il déjà un humain pour faire cela ? npm et GitHub ne peuvent
pas y répondre (`PRODUCT.md` §5).

---

## 4. Ce que ces seuils ne prétendent pas être

- **500 téléchargements hebdomadaires** est un ordre de grandeur, pas une
  frontière naturelle. Les téléchargements incluent l'intégration continue et
  les miroirs (`DATA.md` §6).
- **6 mois sans commit** ne prouve pas l'abandon. Un dépôt inactif peut être
  achevé. C'est un signal, et il est déclaré comme tel dans les angles morts.
- Aucun de ces trois prédicats ne mesure l'argent. C'est la limite structurelle
  de la v1, affichée dans l'interface.

---

## 5. Journal de calibrage

| Date | Seuil | Avant | Après | Cas déclencheur |
|---|---|---|---|---|
| — | — | — | — | *aucun calibrage effectué — valeurs initiales* |

**Protocole (semaine 9)** : rejouer les 12 à 15 cas de `evals/cases/`, comparer
au verdict attendu écrit à la main, n'ajuster qu'un seuil à la fois, et
inscrire ici le cas qui a motivé chaque déplacement. Un ajustement sans cas
déclencheur n'entre pas dans ce tableau — et n'entre donc pas dans le code.
