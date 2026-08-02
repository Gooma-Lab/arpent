# THRESHOLDS — Arpent

Version 2 · **valeurs non calibrées** — hypothèses de départ, à confronter au
jeu de cas de référence en semaine 9.

---

## 1. Pourquoi ce document existe

`ARCHITECTURE.md` §2 pose que l'application des seuils est déterministe, avec
des « règles figées avant exécution ». `DESIGN.md` §4 donne la signification
des trois verdicts, jamais leurs valeurs. Sans les chiffres, le verdict est
arbitraire.

Ce fichier porte les chiffres. Il est **versionné à chaque calibrage** : toute
modification s'inscrit au journal du §7, avec le cas qui l'a provoquée. Un
seuil qu'on déplace sans dire pourquoi est un seuil qu'on ajuste jusqu'à
obtenir le verdict qui plaît.

## 2. Ce qui est mesuré, et sur quoi

**Tout se calcule sur l'échantillon validé**, jamais sur les résultats bruts
de la recherche.

Cette phrase est la plus importante du document. La sonde du 2 août a montré
que sur la requête `wiki`, les trois paquets les plus téléchargés sont hors
sujet et pèsent deux ordres de grandeur au-dessus du reste : les inclure
n'entache pas la mesure, elle l'inverse.

**Le `total` renvoyé par npm n'est jamais un comptage.** Il annonce 1 211 183
résultats pour « outils de mock pour tests d'API GraphQL ». L'écart entre ce
nombre et le nombre réellement retenu est affiché dans les angles morts, jamais
utilisé dans un calcul.

## 3. Prédicats élémentaires

Appliqués paquet par paquet. Tous les champs viennent de la recherche npm sauf
mention contraire.

| Prédicat | Règle | Source |
|---|---|---|
| `relevant` | retenu par la validation d'instrument | modèle |
| `active` | dernière publication < 12 mois **et** dépôt non archivé | npm + GitHub |
| `maintained` | dernier commit < 6 mois | GitHub |
| `adopted` | ≥ 500 téléchargements hebdomadaires | npm |
| `embedded` | ≥ 10 paquets dépendants | npm (`dependents`) |

**Sans GitHub**, `maintained` est indéterminé et `active` se replie sur la
seule date de publication npm. Le verdict reste rendu, la confiance baisse de
25, et la source manquante est nommée (`DESIGN.md` §6).

## 4. Mesures de forme

C'est l'apport du produit : ce qui ne se lit pas dans les dix premiers
résultats.

| Mesure | Définition | Ce qu'elle dit |
|---|---|---|
| **Concentration** | part des téléchargements captée par le paquet en tête | > 60 % = un dominant ; < 30 % = espace fragmenté |
| **Taux d'abandon** | proportion de paquets pertinents sans commit depuis 24 mois | un espace peuplé mais abandonné n'est pas un espace occupé |
| **Croisement** | le paquet dominant est-il `maintained` ? | **la mesure décisive** |
| **Bande atteignable** | paquets entre 500 et 5 000 dl/semaine | où un entrant peut réalistement se placer |

**Le croisement est la seule mesure qui justifie l'outil.** Dix-sept paquets ne
disent rien. « Le dominant capte 71 % et n'a rien publié depuis dix-neuf
mois » est une décision.

*Cas réel, sonde du 2 août : `next-sitemap`, 634 614 dl/semaine, dernière
publication le 6 septembre 2023.*

⚠️ **La bande atteignable est l'hypothèse la plus fragile de ce document.** Les
bornes 500-5 000 sont transposées d'une mesure faite sur une autre plateforme,
où les ordres de grandeur d'usage n'ont rien à voir. Elles sont à recalibrer en
priorité, et à traiter comme indicatives d'ici là.

## 5. Règles de verdict

Appliquées dans l'ordre du tableau.

| Verdict | Règle |
|---|---|
| **DESERT** | < 3 paquets pertinents **et** maximum de téléchargements < 200 |
| **OPEN** | le paquet dominant n'est pas `maintained`, **ou** taux d'abandon > 60 % |
| **OCCUPIED** | ≥ 2 paquets à la fois `maintained` et `adopted`, dominant inclus |
| **OPEN** *(défaut)* | tout le reste |

OPEN apparaît deux fois volontairement : une fois comme diagnostic positif
— la place est tenue par quelqu'un qui a lâché — et une fois comme cas
résiduel. C'est le verdict qui demande de creuser, donc celui qu'on ne doit
jamais prononcer par enthousiasme.

**Le verdict porte sur l'espace de paquets npm, jamais sur un marché.**
L'interface l'écrit à côté du mot.

**DESERT s'accompagne toujours de la question qui le tranche** : quelqu'un
paie-t-il déjà un humain pour faire cela ? Ni npm ni GitHub ne peuvent y
répondre.

## 6. Ce que ces seuils ne prétendent pas être

- **500 téléchargements hebdomadaires** est un ordre de grandeur. Les
  téléchargements incluent l'intégration continue et les miroirs.
- **6 mois sans commit** ne prouve pas l'abandon. Un dépôt inactif peut être
  achevé.
- **Aucune de ces mesures ne voit l'argent, le canal de distribution, la
  barrière de confiance ou la friction juridique.** Ce sont les quatre causes
  qui ont réellement fermé les pistes explorées, et aucune n'est ici.

## 7. Journal de calibrage

| Date | Seuil | Avant | Après | Cas déclencheur |
|---|---|---|---|---|
| — | — | — | — | *aucun calibrage — valeurs initiales* |

**Protocole (semaine 9)** : rejouer les 12 à 15 cas de `evals/cases/`, comparer
au verdict attendu écrit à la main, n'ajuster qu'un seuil à la fois, inscrire
ici le cas qui a motivé chaque déplacement. Un ajustement sans cas déclencheur
n'entre pas dans ce tableau — et n'entre donc pas dans le code.

**Risque propre à cette version** : une mesure de forme a plus de degrés de
liberté que trois règles. Sur 12 à 15 cas, le sur-ajustement est un danger
réel. Règle de garde : **pas plus d'un paramètre ajusté par cas déclencheur**,
et tout seuil déplacé deux fois est un seuil dont la définition est mauvaise.
