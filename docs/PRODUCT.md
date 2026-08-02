# PRODUCT — Arpent

> Nom retenu : **Arpent**. Disponible sur npm. Organisation GitHub : Gooma Lab.

Version 2 · statut : semaine 1 — squelette en place, boucle d'agent non écrite.

---

## 1. Le problème

Un développeur seul qui envisage de construire un outil perd des semaines à découvrir, après coup, que l'espace est déjà occupé — ou pire, qu'il est vide parce que personne n'en veut.

Regarder les dix premiers résultats d'une recherche npm prend trente secondes et ne demande aucun outil. **Ce qui n'est pas trivial, c'est la forme de l'espace** : la concentration des téléchargements, la proportion de projets abandonnés, et surtout le croisement entre les deux — un espace où le paquet dominant a cessé de publier ne ressemble pas à un espace où cinq paquets maintenus se partagent l'usage.

**Et cette forme est fragile à mesurer.** Une sonde de quinze minutes sur la recherche npm, le 2 août 2026, l'a établi : la requête `wiki` fait remonter `@aws-crypto/crc32` (34 millions de téléchargements hebdomadaires) parce qu'une URL Wikipédia figure dans sa description. Trois des huit premiers résultats sont hors sujet, et ce sont les plus téléchargés de deux ordres de grandeur. Ils **inversent** la conclusion : ils font croire à un espace massivement adopté là où le seul vrai paquet wiki fait 736 téléchargements par semaine.

Dans une question binaire « occupé oui/non », un intrus pèse peu. Dans une analyse de distribution, il décide du résultat.

**Le produit ne résout pas un problème de collecte. Il résout un problème d'interprétation et de vérification** — et il vérifie son propre échantillon avant de conclure, parce que la mesure qu'il produit ne survit pas à un échantillon contaminé.

*Preuve reproductible : `docs/probes/2026-08-02-npm-search.md`.*

## 2. Ce que rend le produit

**La forme d'un espace de paquets, et un verdict qui en découle.**

Le produit tranche, et assume :

- une réponse : occupé / ouvert / désert — **sur l'espace de paquets npm**, pas sur un marché
- les chiffres qui la fondent : concentration des téléchargements, profil de maintenance, et leur croisement
- un niveau de confiance
- la liste explicite de ce que ces sources ne voient pas

**Le croisement est ce qui a de la valeur.** Savoir qu'il existe dix-sept paquets ne dit rien. Savoir que le paquet dominant capte 71 % des téléchargements et n'a rien publié depuis dix-neuf mois est une décision.

*Exemple réel, sonde du 2 août : `next-sitemap`, 634 614 téléchargements hebdomadaires, dernière publication en septembre 2023.*

La dernière ligne — ce que les sources ne voient pas — reste le cœur de la proposition. Un outil qui annonce ses angles morts est plus utile qu'un outil qui prétend tout couvrir. Elle est **courte et constante** : quatre points toujours vrais, pas une grille à moitié vide.

**Ce que le produit ne prétend pas être.** Un instrument de priorisation multi-critères. Il éclaire un signal — l'ouverture — d'une méthode qui en compte dix. Prétendre autre chose serait exactement l'erreur de mesure que le produit combat.

## 3. Personas

**P1 — le constructeur solo** *(usager principal)*
Développeur, 10 h/semaine, envisage de publier un outil. Décision à éclairer : je construis ou je passe à autre chose. Il n'a pas besoin de dix indicateurs, il a besoin de la forme de l'espace — ce que la lecture des dix premiers résultats ne lui donne pas.

*L'auteur du produit est le premier occupant de ce rôle. Ce n'est pas un défaut : c'est ce qui garantit que l'outil est utilisé pour de vrai, et c'est ce que mesure le critère « employé » du §7.*

**P2 — le recruteur technique** *(usager de preuve)*
Consulte l'URL publique pour évaluer une candidature. Ce qu'il vérifie en cinq minutes : est-ce joignable, est-ce que l'échec est géré, est-ce mesuré, est-ce que ça sert quelqu'un.

**P3 — le lecteur du baromètre** *(usager futur, v2+)*
Professionnel qui consomme les mesures agrégées sans utiliser l'outil.

## 4. Périmètre v1

**Inclus**
- Écosystème JavaScript / TypeScript
- Bibliothèques et outils en ligne de commande publiés
- Sources : registre npm, API GitHub

**Exclu de la v1**
- SaaS, extensions de navigateur, applications
- Autres écosystèmes de paquets (PyPI, crates.io) — v2, sans refonte
- Places de marché (Apify et assimilés) — répondent à une autre question

**Hors périmètre définitif**
- Tout ce qui touche au retail, au commerce de détail, au service après-vente ou à la réparation. Contrainte externe, non négociable.

## 5. Limites structurelles, assumées et affichées

Quatre points, toujours vrais, affichés dans l'interface à chaque verdict et non seulement ici.

**L'argent.** Ni npm ni GitHub ne mesurent un revenu. L'outil dit « personne n'a publié ça » ou « ceux qui l'ont fait ont cessé de maintenir ». Jamais « quelqu'un paie ».

**Le canal de distribution.** Un concurrent peut être adoubé par un prescripteur — une fédération, un annuaire, un intégrateur — sans que rien n'apparaisse dans un registre de paquets. C'est ce qui a fermé quatre pistes lors de l'exploration, et aucune ne l'aurait été par cet outil.

**La barrière de confiance.** Certains achats exigent une antériorité, une société, une assurance. Invisible ici.

**La friction juridique.** Un statut réglementaire peut rendre une piste inexploitable pour un solo. Invisible ici.

C'est donc un **filtre d'élimination rapide sur un signal, pas une validation commerciale**.

**Une limite d'instrument, distincte des précédentes.** Le `total` renvoyé par la recherche npm n'est pas un comptage de l'espace : la requête « outils de mock pour tests d'API GraphQL » en annonce 1 211 183. Le nombre de paquets pertinents provient exclusivement de l'échantillon validé, et l'écart est affiché.

La première limite sera partiellement levée en v2 : une offre d'emploi est le signal d'argent le plus direct qui existe, puisque quelqu'un s'engage à verser un salaire. **France Travail est la seule source d'emploi ayant été vérifiée** — l'APEC n'expose pas d'API publique, et les autres n'ont pas été examinées.

## 6. Proposition de valeur

| Pour qui | Valeur |
|---|---|
| P1 | Donne en deux minutes la forme d'un espace — concentration, abandon, croisement — que la lecture des dix premiers résultats ne donne pas |
| P2 | Preuve vérifiable d'une compétence d'ingénierie agentique, mesurée et budgétée |
| P3 | Mesures inédites — personne ne publie ce croisement npm × GitHub |

**Différenciation** : les outils existants rendent des métriques. Celui-ci rend un jugement, **et il vérifie son propre échantillon avant de le rendre** — parce qu'une mesure de distribution ne survit pas à un échantillon contaminé, ce qui a été établi et non supposé.

## 7. Critères de réussite

| Critère | Seuil |
|---|---|
| Joignable | Une URL publique répond |
| Utile | Verdict rendu en moins de 2 minutes |
| Honnête | Chaque verdict porte un niveau de confiance et ses angles morts |
| **Employé** | **Au moins 5 exécutions consignées dans le journal de méthode, dont une ayant changé une décision** |

**Sur le critère « employé ».** Il exigeait auparavant un usage par un tiers. L'auteur étant le premier usager de l'outil, cette formulation aurait rendu le critère dépendant d'un problème de distribution étranger au produit. Un usage propre et documenté est plus honnête, et plus fort à démontrer : « l'outil a écarté trois de mes pistes en deux minutes chacune » vaut mieux qu'un essai anonyme. Un usage par un tiers reste un bonus, pas le seuil.

**Échec** : après 12 semaines, rien n'est joignable publiquement. Dans ce cas, réduire le périmètre — pas glisser le calendrier.

## 8. Feuille de route

- **v1** — npm + GitHub, écosystème JS/TS
- **v2** — source France Travail (signal d'argent), autres registres de paquets
- **v3** — publication du serveur MCP exposant l'outil à d'autres agents
