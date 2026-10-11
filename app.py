import os

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory

DOSSIER = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(DOSSIER, "website")

app = Flask(
    __name__,
    template_folder=os.path.join(SITE, "templates"),
    static_folder=os.path.join(SITE, "static"),
    static_url_path="",
)
app.json.ensure_ascii = False

# Modèle chargé une seule fois au démarrage
CHEMIN_MODELE = os.path.join(DOSSIER, "model", "model.joblib")
if not os.path.exists(CHEMIN_MODELE):
    raise SystemExit("Fichier model.joblib introuvable. Lancez d'abord python model/train_model.py.")
_artefact = joblib.load(CHEMIN_MODELE)
MODELE = _artefact["modele"]
COLONNES = _artefact["colonnes"]

# Mêmes valeurs que house_pred.csv
VILLES = ["Paris", "Lyon", "Lille", "Marseille", "Rennes", "Bordeaux", "Strasbourg"]
ETATS = ["mauvais", "moyen", "bon", "excellent"]
DPE = ["A", "B", "C", "D", "E", "F", "G"]
TYPES = ["appartement", "maison"]
OUI_NON = ["oui", "non"]

# Notebook : 49,99 € TTC par estimation, réglés avant le calcul du moteur.
PRIX_ESTIMATION_TTC = 49.99


def prix_affiche():
    return f"{PRIX_ESTIMATION_TTC:.2f}".replace(".", ",")


# nom, minimum, maximum, entier, message si hors plage
NOMBRES = [
    ("surface", 15, 250, False, "La surface doit être comprise entre 15 et 250 m²."),
    ("nb_pieces", 1, 12, True, "Le nombre de pièces doit être compris entre 1 et 12."),
    ("nb_chambres", 1, 10, True, "Le nombre de chambres doit être compris entre 1 et 10."),
    ("nb_salles_de_bain", 1, 5, True, "Le nombre de salles de bain doit être compris entre 1 et 5."),
    ("etage", 0, 20, True, "L'étage doit être compris entre 0 et 20."),
    ("annee_construction", 1900, 2025, True, "L'année de construction doit être comprise entre 1900 et 2025."),
    ("distance_centre", 0, 30, False, "La distance au centre doit être comprise entre 0 et 30 km."),
]
CATEGORIES = [
    ("type_bien", TYPES, "Le type de bien doit être « appartement » ou « maison »."),
    ("ville", VILLES, "La ville n'est pas reconnue."),
    ("etat", ETATS, "L'état doit être mauvais, moyen, bon ou excellent."),
    ("dpe", DPE, "Le DPE doit être une lettre de A à G."),
    ("garage", OUI_NON, "Le garage doit valoir oui ou non."),
    ("ascenseur", OUI_NON, "L'ascenseur doit valoir oui ou non."),
    ("balcon_terrasse", OUI_NON, "Le balcon ou la terrasse doit valoir oui ou non."),
    ("cave", OUI_NON, "La cave doit valoir oui ou non."),
]


def lire_nombre(donnees, nom, mini, maxi, entier, message):
    if nom not in donnees:
        raise ValueError(f"Champ manquant : {nom}.")
    valeur = donnees[nom]
    # bool est un int en Python : on le refuse
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        raise ValueError(f"Le champ {nom} doit être un nombre.")
    if entier and int(valeur) != valeur:
        raise ValueError(f"Le champ {nom} doit être un entier.")
    if valeur < mini or valeur > maxi:
        raise ValueError(message)
    return int(valeur) if entier else float(valeur)


def lire_categorie(donnees, nom, autorisees, message):
    if nom not in donnees:
        raise ValueError(f"Champ manquant : {nom}.")
    valeur = donnees[nom]
    if not isinstance(valeur, str) or valeur.strip() not in autorisees:
        raise ValueError(message)
    return valeur.strip()


def valider(donnees):
    if not isinstance(donnees, dict):
        raise ValueError("Corps JSON attendu.")
    ligne = {}
    for nom, mini, maxi, entier, message in NOMBRES:
        ligne[nom] = lire_nombre(donnees, nom, mini, maxi, entier, message)
    for nom, autorisees, message in CATEGORIES:
        ligne[nom] = lire_categorie(donnees, nom, autorisees, message)
    # Mêmes règles dures que generate_data.py
    if ligne["nb_pieces"] <= 2 and ligne["nb_chambres"] != 1:
        raise ValueError("Un studio ou un deux-pièces compte une seule chambre.")
    if ligne["nb_pieces"] == 3 and ligne["nb_chambres"] != 2:
        raise ValueError("Un trois-pièces compte deux chambres : la troisième pièce est le séjour.")
    if ligne["nb_pieces"] >= 4 and ligne["nb_chambres"] not in (ligne["nb_pieces"] - 1, ligne["nb_pieces"] - 2):
        raise ValueError("Au-delà de trois pièces, comptez le séjour et au plus une seconde pièce de vie.")
    if ligne["nb_salles_de_bain"] > ligne["nb_chambres"]:
        raise ValueError("Il ne peut pas y avoir plus de salles de bain que de chambres.")
    if ligne["nb_salles_de_bain"] >= 2 and (ligne["surface"] < 75 or ligne["nb_chambres"] < 2):
        raise ValueError("Une seconde salle de bain demande au moins 2 chambres et 75 m².")
    if ligne["nb_salles_de_bain"] >= 3 and (ligne["surface"] < 120 or ligne["nb_chambres"] < 3):
        raise ValueError("Trois salles de bain demandent au moins 3 chambres et 120 m².")
    # Mêmes seuils que generate_data.py : 18, 32, 48, 70, 90, 110, 130, 150 m²
    seuils_pieces = (18, 32, 48, 70, 90, 110, 130, 150)
    pieces_max = 1
    for n, seuil in enumerate(seuils_pieces, start=1):
        if ligne["surface"] >= seuil:
            pieces_max = n
    if ligne["nb_pieces"] > pieces_max:
        raise ValueError("La surface est trop petite pour ce nombre de pièces.")
    if ligne["type_bien"] == "maison" and ligne["etage"] != 0:
        raise ValueError("Une maison se saisit à l'étage 0.")
    if ligne["type_bien"] == "maison" and ligne["ascenseur"] == "oui":
        raise ValueError("Une maison n'a pas d'ascenseur.")
    if ligne["annee_construction"] >= 2015 and ligne["etat"] == "mauvais":
        raise ValueError("Un logement construit à partir de 2015 n'est pas en mauvais état.")
    if ligne["annee_construction"] >= 2022 and ligne["dpe"] not in DPE[:2]:
        raise ValueError("Un logement construit à partir de 2022 a un DPE A ou B.")
    if ligne["annee_construction"] >= 2013 and ligne["dpe"] in ("F", "G"):
        raise ValueError("Un logement construit à partir de 2013 n'est pas en DPE F ou G.")
    return ligne


def estimer_prix(ligne):
    # Même encodage qu'à l'entraînement, colonnes remises dans l'ordre
    tableau = pd.DataFrame([ligne])
    encode = pd.get_dummies(tableau).astype(float)
    encode = encode.reindex(columns=COLONNES, fill_value=0)
    return int(round(float(MODELE.predict(encode)[0])))


@app.route("/")
def home():
    return render_template("index.html", prix=prix_affiche())


@app.route("/estimation")
def page_estimation():
    return render_template("estimation.html", prix=prix_affiche())


@app.route("/redfile_logo.png")
def logo():
    return send_from_directory(os.path.join(SITE, "static", "images"), "redfile_logo.png")


@app.route("/estimate", methods=["POST"])
def estimate():
    donnees = request.get_json(silent=True)
    if not isinstance(donnees, dict) or donnees.get("paiement") is not True:
        return jsonify({
            "erreur": f"Réglez d'abord l'estimation : {prix_affiche()} € TTC.",
            "tarif_ttc": PRIX_ESTIMATION_TTC,
        }), 402
    try:
        ligne = valider(donnees)
    except ValueError as erreur:
        return jsonify({"erreur": str(erreur)}), 400
    return jsonify({
        "estimation": estimer_prix(ligne),
        "tarif_ttc": PRIX_ESTIMATION_TTC,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
