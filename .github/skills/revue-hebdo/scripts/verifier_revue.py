"""Vérifie une revue des conversations contre ses chiffres. Exit 0 si conforme, 2 sinon.

Usage : python verifier_revue.py revue/semaine_01
Fichier figé : on ne le modifie pas pour faire passer une revue.
"""
import json
import re
import sys
from pathlib import Path

SECTIONS = ["Synthèse", "Conversion", "Règles du bot", "Pour l'équipe produit", "Décision attendue"]
IDENTIFIANT = re.compile(r"\bC\d{2}-\d+\b")
SEMAINE = re.compile(r"semaine_\d+")
NOMBRE = re.compile(r"\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?")
COMMENTAIRE = re.compile(r"<!--.*?-->", re.S)


def valeurs(objet):
    """Tous les nombres de chiffres.json, en valeur absolue."""
    if isinstance(objet, bool) or objet is None:
        return set()
    if isinstance(objet, (int, float)):
        return {round(abs(float(objet)), 2)}
    if isinstance(objet, dict):
        objet = list(objet.values())
    if isinstance(objet, list):
        return set().union(*(valeurs(element) for element in objet)) if objet else set()
    return set()


def conclure(erreurs):
    for erreur in dict.fromkeys(erreurs):
        print(f"ERREUR: {erreur}")
    print("VERIFICATION: ECHEC" if erreurs else "VERIFICATION: OK")
    sys.exit(2 if erreurs else 0)


def main():
    if len(sys.argv) != 2:
        print("Usage : python verifier_revue.py revue/semaine_NN")
        sys.exit(2)
    dossier = Path(sys.argv[1])
    chemin_chiffres, chemin_revue = dossier / "chiffres.json", dossier / "revue.md"
    erreurs = [f"{c.as_posix()} absent" for c in (chemin_chiffres, chemin_revue) if not c.is_file()]
    if erreurs:
        conclure(erreurs)

    chiffres = json.loads(chemin_chiffres.read_text(encoding="utf-8"))
    texte = COMMENTAIRE.sub("", chemin_revue.read_text(encoding="utf-8"))

    titres = [ligne[3:].strip() for ligne in texte.splitlines() if ligne.startswith("## ")]
    if titres != SECTIONS:
        erreurs.append("sections attendues, dans cet ordre : " + " / ".join(SECTIONS))

    for conversation in chiffres["conversations"]:
        if conversation["id"] not in texte:
            erreurs.append(f"conversation absente : {conversation['id']}")

    autorises = valeurs(chiffres)
    sans_codes = SEMAINE.sub("", IDENTIFIANT.sub("", texte))
    for jeton in NOMBRE.findall(sans_codes):
        propre = re.sub(r"[ \u00a0\u202f]", "", jeton).replace(",", ".")
        if round(float(propre), 2) not in autorises:
            lisible = re.sub(r"[\u00a0\u202f]", " ", jeton)
            erreurs.append(f"chiffre absent de chiffres.json : {lisible}")

    conclure(erreurs)


if __name__ == "__main__":
    main()
