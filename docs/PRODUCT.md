# PRODUCT — Arpent

> Nom retenu : **Arpent**. Disponible sur npm. Organisation GitHub : Gooma Lab.

Version 2 · statut : semaine 1 — squelette en place, boucle d'agent non écrite.

---

## 1. Le problème

Un développeur seul qui envisage de construire un outil perd des semaines à découvrir, après coup, que l'espace est déjà occupé — ou pire, qu'il est vide parce que personne n'en veut.

L'information existe (registres publics, dépôts, statistiques d'usage) mais elle est dispersée, et **la lire est plus difficile que la collecter**. Deux mesures produites pendant la phase d'exploration de ce projet étaient fausses, non par manque de données, mais par défaut d'instrument : une requête censée porter sur les wikis remontait des extracteurs de réseaux sociaux, et une note moyenne agrégeait des zéros correspondant à des projets simplement non notés.

**Le produit ne résout pas un problème de collecte. Il résout un problème d'interprétation et de vérification.**

## 2. Ce que rend le produit

**Un verdict, pas un tableau de bord.**

Un tableau de bord reporte l'interprétation sur l'usager. Le produit tranche, et assume :

- une réponse : occupé / ouvert / désert
- un niveau de confiance
- la liste explicite de ce qui n'a pas pu être mesuré

Cette troisième ligne est le cœur de la proposition de valeur. Un outil qui annonce ses angles morts est plus utile qu'un outil qui prétend tout couvrir.

## 3. Personas

**P1 — le constructeur solo** *(usager principal)*
Développeur, 10 h/semaine, envisage de publier un outil. Décision à éclairer : je construis ou je passe à autre chose. Il n'a pas besoin de dix indicateurs, il a besoin d'arrêter de perdre du temps sur un espace saturé.

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

## 5. Limite structurelle, assumée et affichée

**npm et GitHub mesurent l'adoption. Jamais l'argent.**

L'outil ne peut pas dire « quelqu'un paie pour ça ». Il dit « personne n'a construit ça » ou « ceux qui l'ont fait ont cessé de maintenir ».

C'est donc un **filtre d'élimination rapide, pas une validation commerciale**. Cette limite est affichée dans l'interface, pas seulement dans la documentation.

Elle sera partiellement levée en v2 : une offre d'emploi est le signal d'argent le plus direct qui existe, puisque quelqu'un s'engage à verser un salaire. La source France Travail est identifiée pour cela.

## 6. Proposition de valeur

| Pour qui | Valeur |
|---|---|
| P1 | Élimine en deux minutes une piste qui aurait coûté six semaines |
| P2 | Preuve vérifiable d'une compétence d'ingénierie agentique |
| P3 | Mesures inédites — personne ne publie ce croisement npm × GitHub |

**Différenciation** : les outils existants rendent des métriques. Celui-ci rend un jugement, et il vérifie son propre instrument avant de le rendre.

## 7. Critères de réussite

| Critère | Seuil |
|---|---|
| Joignable | Une URL publique répond |
| Utile | Verdict rendu en moins de 2 minutes |
| Honnête | Chaque verdict porte un niveau de confiance et ses angles morts |
| Employé | Au moins un usage réel documenté par un tiers |

**Échec** : après 10 semaines, rien n'est joignable publiquement. Dans ce cas, réduire le périmètre — pas glisser le calendrier.

## 8. Feuille de route

- **v1** — npm + GitHub, écosystème JS/TS
- **v2** — source France Travail (signal d'argent), autres registres de paquets
- **v3** — publication du serveur MCP exposant l'outil à d'autres agents
