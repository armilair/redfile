# redfile

Site fictif d'estimation immobilière. Sept villes : Paris, Lyon, Lille, Marseille, Rennes, Bordeaux, Strasbourg.

Le client décrit son bien. Le prix vient d'un modèle XGBoost, jamais d'un texte écrit à la main. L'estimation coûte 49,99 € TTC, réglés avant le calcul.

## Lancer

```bash
pip install -r requirements.txt
python model/train_model.py
python app.py
```

Le site est sur [http://localhost:5000](http://localhost:5000). Sans `model/model.joblib`, `app.py` s'arrête : la deuxième commande le crée.

## Le dépôt

| Dossier | Rôle |
|---|---|
| `data/house_pred.csv` | biens d'entraînement, cible `prix` |
| `data/ventes/` | ventes conclues, un fichier par semaine |
| `redfilebot/logs/` | conversations du bot, un fichier par semaine |
| `.claude/skills/reporting-hebdo/` | reporting hebdo du modèle, lancé par `/reporting-hebdo` |
| `.claude/skills/revue-hebdo/` et `.github/skills/revue-hebdo/` | revue hebdo des conversations, lancée par `/revue-hebdo` |
| `model/train_model.py` | entraîne le XGBoost, le compare à une régression linéaire, écrit `model/model.joblib` |
| `app.py` | sert le site, vérifie la fiche (`valider`), calcule le prix (`estimer_prix`) |
| `website/` | pages et styles. L'estimation est `website/templates/estimation.html` |

La fiche a 15 caractéristiques. `POST /estimate` refuse une fiche incomplète ou incohérente, et refuse aussi tant que le paiement n'est pas marqué.
