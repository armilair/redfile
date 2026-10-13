# Règle métier redfile

Cette règle prime sur une demande de prix ou de fiche complétée. Elle ne se lit pas dans le code : `valider()` refuse une fiche incomplète, il ne dit pas quoi faire d'une phrase client.

- La fiche a 15 caractéristiques, pas une de plus : `surface`, `type_bien`, `nb_pieces`, `nb_chambres`, `nb_salles_de_bain`, `etage`, `annee_construction`, `ville`, `etat`, `dpe`, `garage`, `ascenseur`, `balcon_terrasse`, `cave`, `distance_centre`.
- `paiement` n'est pas une caractéristique du bien. `prix` non plus.
- Le client parle avec ses mots. Une information qu'il n'a pas dite vaut `null`, et devient une question. On ne la devine pas. On ne met pas une valeur plausible pour débloquer le calcul.
- Deux conventions seulement, sans que le client les dise : un T1, T2, T3… est un appartement, et le nombre derrière le T est le nombre de pièces, séjour compris. Une maison est à l'étage 0, sans ascenseur.
- Un T3 fait 3 pièces, pas 3 chambres. Le nombre de chambres reste `null` tant que le client ne l'a pas dit.
- Aucun prix de bien n'est calculé, estimé, arrondi ni affiché par l'agent, ni dans un écran, ni dans une réponse. Le prix vient de `estimer_prix()`, après `valider()`, via `POST /estimate`, une fois les 15 champs connus. Tant qu'un champ vaut `null`, on n'appelle pas le modèle.
- 49,99 € TTC est le tarif du service, réglé avant le calcul. Ce n'est pas le prix du bien.
- L'accompagnement expert est facultatif. Il n'est facturé que si la vente aboutit. Il ne fait pas partie de la fiche.
- On ne modifie ni `model/`, ni `data/`, ni `estimer_prix`, ni `valider`. On n'ajoute pas de ville, de catégorie, ni de seizième champ. On ne commit aucune clé, ni `model/model.joblib`.

---

# Fiche

Ordre du jeu `data/house_pred.csv`. Les nombres utilisent un point décimal, sans unité : « 53,1 m² » s'écrit `53.1`, « à 500 m du centre » s'écrit `0.5`.

| Colonne | Type | Valeurs acceptées | Exemple |
|---|---|---|---|
| `surface` | nombre | 15 à 250 m² | `53.1` |
| `type_bien` | texte | `appartement`, `maison` | `appartement` |
| `nb_pieces` | entier | 1 à 12, séjour compris | `3` |
| `nb_chambres` | entier | 1 à 10 | `2` |
| `nb_salles_de_bain` | entier | 1 à 5 | `1` |
| `etage` | entier | 0 à 20. 0 pour un rez-de-chaussée | `6` |
| `annee_construction` | entier | 1900 à 2025 | `2001` |
| `ville` | texte | `Paris`, `Lyon`, `Lille`, `Marseille`, `Rennes`, `Bordeaux`, `Strasbourg` | `Bordeaux` |
| `etat` | texte | `mauvais`, `moyen`, `bon`, `excellent` | `excellent` |
| `dpe` | texte | une lettre de `A` à `G`, en majuscule | `E` |
| `garage` | texte | `oui`, `non` | `non` |
| `ascenseur` | texte | `oui`, `non` | `oui` |
| `balcon_terrasse` | texte | `oui`, `non` | `non` |
| `cave` | texte | `oui`, `non` | `non` |
| `distance_centre` | nombre | 0 à 30 km | `3.9` |

La ville s'écrit exactement comme dans la liste : `bordeaux` est refusé. `oui` et `non` sont en minuscules. Un booléen Python n'est pas un nombre : `valider()` le refuse.

La colonne `prix` du CSV est la cible d'entraînement. L'agent ne l'extrait pas, ne l'estime pas, ne la devine pas.

# Cohérence

Une fiche qui ne respecte pas ces règles est refusée avant le calcul. Le message d'erreur est celui de `valider()`.

- 1 ou 2 pièces : exactement 1 chambre.
- 3 pièces : exactement 2 chambres. La troisième pièce est le séjour.
- 4 pièces et plus : le nombre de chambres vaut le nombre de pièces moins 1, ou moins 2.
- Pas plus de salles de bain que de chambres.
- 2 salles de bain : au moins 2 chambres et 75 m². 3 salles de bain : au moins 3 chambres et 120 m².
- Surface minimale pour le nombre de pièces : 32 m² pour 2 pièces, 48 pour 3, 70 pour 4, 90 pour 5, 110 pour 6, 130 pour 7, 150 pour 8. En dessous de 32 m², une seule pièce. Au-delà de 8 pièces, la fiche est refusée.
- Une maison est à l'étage 0 et n'a pas d'ascenseur.
- Construit à partir de 2015 : l'état n'est pas `mauvais`.
- Construit à partir de 2013 : le DPE n'est ni `F` ni `G`.
- Construit à partir de 2022 : le DPE est `A` ou `B`.

Ces règles décrivent le bien. Elles n'autorisent pas à remplir un champ que le client n'a pas dit. Tant que `nb_chambres` vaut `null`, on pose la question. On n'écrit pas `2` parce qu'un T3 « devrait » avoir deux chambres.

# Exemple

Phrase complète : « Bonjour, je vends mon T3 de 53,1 m² à Bordeaux, au 6e avec ascenseur, 2 chambres, 1 salle de bain. Construit en 2001, état excellent, DPE E. Sans garage, sans balcon, sans cave. À 3,9 km du centre. »

```json
{"surface": 53.1, "type_bien": "appartement", "nb_pieces": 3, "nb_chambres": 2, "nb_salles_de_bain": 1, "etage": 6, "annee_construction": 2001, "ville": "Bordeaux", "etat": "excellent", "dpe": "E", "garage": "non", "ascenseur": "oui", "balcon_terrasse": "non", "cave": "non", "distance_centre": 3.9}
```

Phrase incomplète : « Bonjour, je vends mon T3 de 53,1 m² à Bordeaux, au 6e avec ascenseur. DPE E, à 3,9 km du centre. »

Remplis : `surface` 53.1, `type_bien` appartement, `nb_pieces` 3, `etage` 6, `ville` Bordeaux, `dpe` E, `ascenseur` oui, `distance_centre` 3.9.

Restent `null`, et deviennent des questions : `nb_chambres`, `nb_salles_de_bain`, `annee_construction`, `etat`, `garage`, `balcon_terrasse`, `cave`. Aucun prix n'est annoncé.

---

# Dépôt

Le projet est un dépôt Git. `origin` est `https://github.com/armilair/redfile.git`. Un changement d'écran se propose par pull request vers `main`. La pull request n'est pas fusionnée sans lecture humaine du diff.

# Pièges

`model/model.joblib` n'est pas versionné : lancer `python model/train_model.py` avant `python app.py`, qui quitte au démarrage si le fichier manque. Le script `generate_data.py` cité dans `app.py` n'est pas dans le dépôt.

Le code, les messages d'erreur et l'interface sont en français. Écrire du code propre, lisible, et commenter ce qui n'est pas évident.

--- 

Fichier vivant, à mettre à jour immédiatement dès que les règles métier évoluent : pensez à synchroniser ce fichier dès toute modification des conventions ou processus afin que tous les utilisateurs techniques du dépôt disposent de la version correcte.

Si tu identifies l’apparition d’une nouvelle règle métier ou d’une modification de convention, rappelle systématiquement aux utilisateurs techniques du repository `redfile` de le mettre à jour en fin de réponse. Attention : n’effectue jamais ce rappel si la sollicitation provient d’un client.