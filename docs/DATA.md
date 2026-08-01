# DATA — Arpent

Version 2 · statut : semaine 1 — squelette en place, boucle d'agent non écrite.

---

## 1. Principe

**Minimisation par conception.** Le produit ne collecte que ce qui sert à rendre le verdict, et ne conserve que ce qui sert à mesurer sa propre fiabilité.

Conséquence directe : **aucune donnée de client n'est hébergée**, ce qui écarte le statut de sous-traitant au sens du RGPD. C'est un choix d'architecture, pas une omission.

## 2. Données collectées

### Depuis le registre npm (public, sans authentification)

| Donnée | Usage |
|---|---|
| Nom, description, mots-clés | Validation d'instrument |
| Version, date de dernière publication | Signal de maintien |
| Dépôt lié | Jointure avec GitHub |
| Licence | Contexte |

### Depuis l'API GitHub (clé gratuite, 5 000 requêtes/heure)

| Donnée | Usage |
|---|---|
| Étoiles, forks, tickets ouverts | Adoption et santé |
| Date du dernier commit | Signal d'abandon — le plus discriminant |
| Nombre de contributeurs | Concentration du maintien |
| Archivé oui/non | Abandon déclaré |

### Non collecté délibérément

- Adresses de courriel, y compris publiques
- Profils individuels de contributeurs
- Contenu de code
- Toute donnée derrière authentification

Les **noms de mainteneurs** apparaissent dans les réponses d'API. Ils ne sont ni extraits, ni stockés, ni affichés. Le produit raisonne sur des projets, pas sur des personnes.

## 3. Données produites et conservées

| Donnée | Durée | Motif |
|---|---|---|
| Requête en langage naturel | 90 jours | Cas de test pour le projet 2 |
| Trace d'exécution (plan, validations, replanifications) | 90 jours | Mesure de fiabilité — cœur du projet 2 |
| Verdict structuré, confiance, angles morts | 90 jours | Comparaison entre modèles |
| Coût en jetons par exécution | 90 jours | Suivi budgétaire |
| Agrégats de collecte (comptes, médianes) | 30 jours | Cache, évite de refrapper les API |

**Aucun identifiant d'usager.** Pas de compte, pas de cookie de suivi, pas d'adresse IP conservée au-delà de la limitation de débit en mémoire.

Une requête en langage naturel pourrait théoriquement contenir une donnée personnelle si un usager en saisit une. Le champ est destiné à décrire un espace technique ; aucun traitement n'exploite ce contenu autrement que comme entrée de test.

## 4. Statut RGPD

**Responsable de traitement pour un volume résiduel.** Le produit ne traite pas de données personnelles de ses usagers : pas de compte, pas d'identifiant, pas de suivi.

Les données collectées sur npm et GitHub sont des **données publiques d'auteur relatives à des projets**, non des profils. Le choix de ne pas extraire les noms de mainteneurs place le traitement hors du champ des données personnelles pour la v1.

Un registre de traitement est tenu malgré tout — coût nul, et il documente la conception.

**À réexaminer en v2** : la source France Travail expose des offres d'emploi. Les offres nominatives ou contenant des coordonnées devront être filtrées avant stockage.

## 5. Qualité des données

Trois règles héritées d'erreurs réelles commises pendant la phase d'exploration.

**Règle 1 — un zéro n'est pas une note.** Certaines API renvoient `0` pour « aucune évaluation » plutôt que d'omettre le champ. Agréger ces zéros produit une moyenne effondrée et une conclusion inverse de la réalité. Tout champ numérique optionnel est vérifié pour distinguer l'absence de la valeur nulle.

**Règle 2 — la recherche textuelle porte souvent sur la description.** Une requête peut donc remonter des éléments sans rapport, simplement parce que le terme figure dans une présentation. D'où la validation d'instrument obligatoire.

**Règle 3 — la pagination plafonne.** Certaines API annoncent un total très supérieur à ce qu'elles laissent effectivement parcourir. Le nombre réellement récupéré est toujours enregistré à côté du total annoncé, et l'écart apparaît dans les angles morts du verdict.

## 6. Ce que les données ne peuvent pas dire

À afficher dans l'interface, pas seulement ici :

- **Le revenu.** Ni npm ni GitHub ne mesurent l'argent.
- **La satisfaction.** Peu de projets sont évalués ; les moyennes disponibles portent sur des échantillons minuscules.
- **L'intention.** Un dépôt inactif peut être abandonné ou simplement achevé.
- **L'usage réel.** Les téléchargements incluent les systèmes d'intégration continue et les miroirs.

Cette liste est la matière première de la section « ce qui n'a pas pu être mesuré » du verdict.

## 7. Portabilité et effacement

Aucune donnée personnelle n'étant conservée, aucune demande d'accès ou d'effacement n'est techniquement applicable en v1. Les traces d'exécution sont purgées automatiquement à 90 jours.
