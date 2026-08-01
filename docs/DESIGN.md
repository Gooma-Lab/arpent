# DESIGN — Arpent

Version 2 · statut : semaine 1 — squelette en place, boucle d'agent non écrite.

---

## 1. Principe

**L'incertitude est un élément d'interface de premier plan, pas une note de bas de page.**

Un verdict sans niveau de confiance ne vaut rien : il invite à croire une mesure dont l'usager ne peut pas évaluer la solidité. C'est exactement le mécanisme qui a produit deux conclusions fausses pendant la phase d'exploration.

Corollaire : ce que l'outil n'a pas pu mesurer s'affiche **au même niveau visuel** que ce qu'il a mesuré.

## 2. Parcours

Un écran, trois états.

**Saisie** — un champ unique en langage naturel, avec trois exemples cliquables. Pas de formulaire, pas de filtres : la décomposition est le travail de l'agent.

**Progression** — les étapes s'affichent en temps réel. Ce n'est pas cosmétique : voir « validation de l'instrument… échantillon non pertinent, replanification » est la meilleure démonstration possible de ce que fait le produit. Un recruteur comprend le projet sans lire le code.

**Verdict** — structuré comme suit.

## 3. Structure du verdict

```
┌──────────────────────────────────────────┐
│  OCCUPÉ                    confiance 80 % │
│                                          │
│  14 paquets actifs, dont 4 maintenus     │
│  au cours des 6 derniers mois.           │
├──────────────────────────────────────────┤
│  CE QUI FONDE CE VERDICT                 │
│  • …                                     │
├──────────────────────────────────────────┤
│  CE QUI N'A PAS PU ÊTRE MESURÉ           │
│  • Personne ne paie-t-il ? Non mesurable │
│    par npm et GitHub.                    │
│  • …                                     │
├──────────────────────────────────────────┤
│  ÉCHANTILLON VÉRIFIABLE                  │
│  Les 5 premiers résultats, en clair.     │
└──────────────────────────────────────────┘
```

**L'échantillon vérifiable est obligatoire et non repliable.** Il permet à l'usager de contrôler l'instrument en dix secondes, exactement comme le contrôle qui manquait aux mesures fautives d'origine.

*Le 80 de cette maquette n'est pas décoratif : c'est 95 − 10 (plafond de
pagination atteint) − 5 (téléchargements manquants sur plus d'un quart de
l'échantillon). Tout chiffre affiché doit être reconstituable à partir du §5 —
sinon il n'a pas sa place dans ce produit.*

## 4. Les trois verdicts

| Verdict | Signification | Ce que l'usager en fait |
|---|---|---|
| **OCCUPÉ** | Acteurs actifs et maintenus | Passer, ou identifier un segment délaissé |
| **OUVERT** | Peu d'acteurs, ou acteurs abandonnés | Creuser — mais vérifier le signal d'argent ailleurs |
| **DÉSERT** | Presque rien, et rien n'a jamais pris | Se méfier : absence de problème, pas d'opportunité |

Les seuils chiffrés qui produisent ces trois valeurs sont dans
`THRESHOLDS.md`, avec leur journal de calibrage. Ce tableau donne le sens ; ce
fichier-là donne les nombres.

La distinction OUVERT / DÉSERT est le second apport du produit. Elle évite le piège symétrique de la saturation : conclure à une opportunité là où il n'y a qu'un marché sans demande.

Le verdict DÉSERT s'accompagne systématiquement de la question qui le tranche : quelqu'un paie-t-il déjà un humain pour faire cela ?

## 5. Confiance

Calculée de façon déterministe, jamais estimée par le modèle. Score de départ
**95** — jamais 100 : c'est une mesure, pas une certitude.

| Pénalité | Points |
|---|---|
| Par replanification | −20 (maximum −40) |
| Par source indisponible | −25 |
| Échantillon jugé « partiellement pertinent » par le validateur | −15 |
| Plafond de pagination atteint (total annoncé ≫ récupéré) | −10 |
| Moins de 50 % des paquets résolus vers un dépôt GitHub | −10 |
| Données de téléchargement manquantes sur > 25 % de l'échantillon | −5 |

Plancher **10**. Chaque pénalité appliquée est **nommée dans la trace et
affichable** : l'usager peut refaire le calcul. Un pourcentage qu'on ne peut
pas reconstituer est exactement le défaut que ce produit prétend corriger.

Les trois paliers ne sont plus la règle mais **l'étiquette** du score :

- **Élevée** — supérieure à 75
- **Moyenne** — de 50 à 75
- **Faible** — inférieure à 50

Sous 50, le verdict est rendu mais visuellement dégradé, avec le motif affiché. **L'outil ne refuse jamais de répondre** — il répond en disant à quel point il est sûr.

## 6. Gestion de l'échec

| Situation | Comportement |
|---|---|
| Une source ne répond pas | Verdict rendu sur les sources restantes, confiance abaissée, source manquante nommée |
| Toutes les sources indisponibles | Message explicite, aucun verdict inventé |
| Demande hors périmètre | Refus explicite, avec rappel du périmètre |
| Demande touchant le retail | Refus, contrainte externe |
| Budget de jetons dépassé | Verdict partiel, avec mention de la troncature |

**Aucun échec silencieux.** Un échec visible et expliqué est un signal de qualité ; un échec masqué est une faute.

## 7. Ce que l'interface n'aura pas

- Pas de compte utilisateur en v1 — usage anonyme, friction minimale
- Pas de graphiques décoratifs — un chiffre lisible bat une visualisation
- Pas d'historique en v1
- Pas de comparaison entre niches — un verdict à la fois

## 8. Accessibilité

Contraste conforme aux critères AA, navigation au clavier, états de chargement annoncés aux lecteurs d'écran. Le coût est nul si c'est prévu dès le départ.
