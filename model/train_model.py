# Entraîne un XGBoost, le compare à une régression linéaire, sauvegarde le modèle.
import os

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

DOSSIER = os.path.dirname(os.path.abspath(__file__))
RACINE = os.path.dirname(DOSSIER)

# 1. Chargement des données
df = pd.read_csv(os.path.join(RACINE, "data", "house_pred.csv"))
y = df["prix"]

# 2. Encodage des catégories (avant le split, pour garder toutes les valeurs)
X = pd.get_dummies(df.drop(columns="prix")).astype(float)

# 3. Découpage 80 % / 20 %
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Entraînement : XGBoost (réglages modestes) et régression linéaire de référence
modele_xgb = XGBRegressor(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.1,
    random_state=42,
    n_jobs=1,
)
modele_xgb.fit(X_train, y_train)
modele_lineaire = LinearRegression()
modele_lineaire.fit(X_train, y_train)

# 5. Métriques sur le jeu de test
modeles = (("Regression lineaire", modele_lineaire), ("XGBoost", modele_xgb))
resultats = {}
for nom, modele in modeles:
    pred = modele.predict(X_test)
    mae = mean_absolute_error(y_test, pred)
    rmse = mean_squared_error(y_test, pred) ** 0.5
    score = r2_score(y_test, pred)
    resultats[nom] = {"mae": mae, "rmse": rmse, "r2": score, "pred": pred}
    print(f"{nom} : MAE {mae:.0f} | RMSE {rmse:.0f} | R2 {score:.3f}")

# 6. Graphique et fichier de métriques
dossier_resultats = os.path.join(DOSSIER, "results")
os.makedirs(dossier_resultats, exist_ok=True)

fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
# Graduations en milliers d'euros, pour que les axes restent lisibles
milliers = FuncFormatter(lambda valeur, _position: f"{valeur / 1000:.0f}")
for ax, nom in zip(axes, ("Regression lineaire", "XGBoost")):
    pred = resultats[nom]["pred"]
    ax.scatter(y_test, pred, alpha=0.75, color="#d01224", s=28)
    bornes = [min(y_test.min(), pred.min()), max(y_test.max(), pred.max())]
    ax.plot(bornes, bornes, color="#1c1917", linewidth=1)
    ax.set_title(f"{nom}  (R2 {resultats[nom]['r2']:.3f})")
    ax.set_xlabel("Prix reel (milliers d'euros)")
    ax.set_ylabel("Prix predit (milliers d'euros)")
    ax.xaxis.set_major_formatter(milliers)
    ax.yaxis.set_major_formatter(milliers)
fig.tight_layout()
fig.savefig(os.path.join(dossier_resultats, "prix_predit_vs_reel.png"), dpi=120)
plt.close(fig)

lignes = ["Metriques sur le jeu de test (20 %, random_state=42)", ""]
for nom in ("Regression lineaire", "XGBoost"):
    m = resultats[nom]
    lignes.append(nom)
    lignes.append(f"MAE  : {m['mae']:.0f} euros")
    lignes.append(f"RMSE : {m['rmse']:.0f} euros")
    lignes.append(f"R2   : {m['r2']:.3f}")
    lignes.append("")
chemin_metriques = os.path.join(dossier_resultats, "metriques.txt")
with open(chemin_metriques, "w", encoding="utf-8") as fichier:
    fichier.write("\n".join(lignes))
print(f"Resultats enregistres dans {dossier_resultats}")

# 7. Un seul artefact : modèle + ordre des colonnes encodées
artefact = {"modele": modele_xgb, "colonnes": list(X.columns)}
chemin_modele = os.path.join(DOSSIER, "model.joblib")
joblib.dump(artefact, chemin_modele)
print(f"Modele enregistre dans {chemin_modele}")
