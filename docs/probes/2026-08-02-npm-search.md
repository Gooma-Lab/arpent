# Sonde — recherche npm, 2 août 2026

**Pourquoi.** Deux jours de construction sans une seule requête réelle. Le
pipeline de la méthode pose que le test réel passe avant la vérification
approfondie ; nous avions inversé l'ordre.

**Coût.** Quinze minutes, zéro euro, aucune clé. Endpoint public
`registry.npmjs.org/-/v1/search`.

**Reproduire** : `curl -s "https://registry.npmjs.org/-/v1/search?text=wiki&size=8"`

---

## Résultat 1 — la contamination par la description se reproduit sur npm

Requête `wiki`, huit premiers résultats :

| Paquet | dl/semaine | Description |
|---|---|---|
| `wiki` | 736 | Federated Wiki |
| `@wry/trie` | **7 605 934** | `https://en.wikipedia.org/wiki/Trie` |
| `@aws-crypto/crc32` | **34 304 010** | `…https://en.wikipedia.org/wiki/…` |
| `@aws-crypto/crc32c` | **24 970 477** | `…https://en.wikipedia.org/wiki/…` |
| `typedoc-github-wiki-theme` | 147 141 | thème TypeDoc |
| `remark-wiki-link` | 19 546 | liens de style wiki |
| `micromark-extension-wiki-link` | 21 949 | liens de style wiki |
| `mdast-util-wiki-link` | 22 072 | liens de style wiki |

**Trois résultats sur huit n'ont aucun rapport avec les wikis.** Ils remontent
parce qu'une URL Wikipédia figure dans leur description — et ce sont les trois
plus téléchargés, de deux ordres de grandeur.

**Conséquence.** Dans une question binaire « occupé oui/non », un intrus pèse
peu. Dans une analyse de distribution, ces trois-là **inversent le résultat** :
ils feraient conclure à un espace massivement adopté là où le seul vrai paquet
wiki fait 736 téléchargements par semaine.

C'est la justification empirique de l'étape de validation d'instrument. Elle ne
repose plus sur l'incident Apify — un cas isolé sur une plateforme hors
périmètre — mais sur deux observations, sur deux plateformes indépendantes,
dont une est notre source réelle.

## Résultat 2 — les requêtes en français se dégradent

| Requête | Résultats notables |
|---|---|
| `graphql mock testing` | `msw`, `mock-apollo-client`, `@apollo/graphql-testing-library`, `@zendesk/laika` — pertinents |
| `outils de mock pour tests d'API GraphQL` | `@gouvfr/dsfr-kit` (système de design de l'État, remonté **parce que sa description est en français**), `@chromatic-com/storybook` (test visuel), `aws-sdk-client-mock` |

**Conséquence.** Le planificateur ne « sélectionne pas des termes » : il
**traduit une intention en mots-clés anglais**. C'est une unité testable
isolément, et c'est le point sur lequel la qualité du produit se joue.

## Résultat 3 — `total` n'est pas un comptage

| Requête | `total` annoncé |
|---|---|
| `outils de mock pour tests d'API GraphQL` | **1 211 183** |
| `graphql mock testing` | 134 453 |
| `sitemap generator` | 79 312 |
| `wiki` | 43 539 |

Ce nombre compte les paquets touchant *un* des mots, pas les paquets de
l'espace. **Il est inutilisable comme mesure d'occupation** et doit être nommé
comme tel dans les angles morts. Le comptage vient exclusivement de
l'échantillon validé.

## Résultat 4 — la réponse contient presque tout

Champs rendus par la recherche, **par paquet et en un seul appel** :

```
package : name, description, keywords, license, version, date, links, publisher
links   : repository, homepage, bugs, npm
hors package : downloads{weekly, monthly}, dependents, score, updated, flags
```

**Conséquence.** Le côté npm d'une exécution coûte **1 à 2 appels HTTP**, pas
un par paquet. Le plafond de 250 appels de D14 avait été dimensionné pour une
architecture inutile.

`dependents` est un signal qui n'avait pas été envisagé : il mesure
l'encastrement réel mieux que les téléchargements, lesquels incluent
l'intégration continue et les miroirs.

## Résultat 5 — le produit fonctionne quand la requête est bonne

Requête `sitemap generator` :

| Paquet | dl/semaine | Dernière publication |
|---|---|---|
| `next-sitemap` | 634 614 | **2023-09-06** |
| `vite-plugin-sitemap` | 62 967 | — |
| `hexo-generator-sitemap` | 7 401 | — |
| `@docmd/plugin-sitemap` | 8 524 | — |
| `@types/sitemap-generator` | 949 | — |

Résultats pertinents, distribution nette, un dominant à dix fois le suivant —
**et ce dominant n'a rien publié depuis près de trois ans.**

C'est exactement le signal que le produit vise : pas « il n'y a personne », mais
« celui qui tient la place a lâché ». Trouvé à la première requête réelle.

---

## Ce que la sonde n'établit pas

- Quatre requêtes. C'est une sonde, pas une mesure de fréquence. Le taux de
  contamination réel reste inconnu et sera mesuré par le taux de
  replanification en semaine 9.
- Rien sur GitHub, dont l'enrichissement n'a pas été testé.
- Rien sur la stabilité dans le temps du classement npm.
