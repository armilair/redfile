"""Vérifie un reporting Marp contre ses chiffres. Exit 0 si conforme, 2 sinon.

Usage : python verifier_reporting.py reporting/semaine_01
Fichier gelé : on ne le modifie pas pour faire passer un reporting.
"""
import json
import re
import sys
from pathlib import Path

NB_SLIDES = 5
VILLES = ["Paris", "Lyon", "Lille", "Marseille", "Rennes", "Bordeaux", "Strasbourg"]
SEPARATEUR = re.compile(r"^ {0,3}(-{3,}|\*{3,}|_{3,})\s*$")
NOMBRE = re.compile(r"\d{1,3}(?:[ \u00a0\u202f]\d{3})+(?:[.,]\d+)?|\d+(?:[.,]\d+)?")
COMMENTAIRE = re.compile(r"<!--.*?-->", re.S)


def valeurs(objet):
    """Tous les nombres de chiffres.json, en valeur absolue."""
    if isinstance(objet, bool):
        return set()
    if isinstance(objet, (int, float)):
        return {round(abs(float(objet)), 2)}
    if isinstance(objet, dict):
        objet = list(objet.values())
    if isinstance(objet, list):
        return set().union(*(valeurs(element) for element in objet)) if objet else set()
    return set()


def decouper(texte, erreurs):
    """Renvoie le texte de chaque slide, en-tête Marp exclu."""
    lignes = texte.splitlines()
    if not lignes or lignes[0].strip() != "---":
        erreurs.append("en-tete Marp absent : la premiere ligne doit etre ---")
        return []
    fin = next((i for i in range(1, len(lignes)) if lignes[i].strip() == "---"), None)
    if fin is None:
        erreurs.append("en-tete Marp non ferme")
        return []
    if not any(ligne.strip() == "marp: true" for ligne in lignes[1:fin]):
        erreurs.append("marp: true absent de l'en-tete")

    slides, courante, dans_code = [], [], False
    for numero, ligne in enumerate(lignes[fin + 1:], start=fin + 2):
        if ligne.strip().startswith("```"):
            dans_code = not dans_code
        if not dans_code and SEPARATEUR.match(ligne):
            if ligne.strip().startswith("-") and courante and courante[-1].strip():
                erreurs.append(f"ligne {numero} : une ligne vide est attendue avant ---")
            slides.append("\n".join(courante))
            courante = []
        else:
            courante.append(ligne)
    slides.append("\n".join(courante))
    return slides


def main():
    if len(sys.argv) != 2:
        print("Usage : python verifier_reporting.py reporting/semaine_NN")
        sys.exit(2)
    dossier = Path(sys.argv[1])
    erreurs = []

    chemin_chiffres = dossier / "chiffres.json"
    chemin_reporting = dossier / "reporting.md"
    if not chemin_chiffres.is_file():
        erreurs.append(f"{chemin_chiffres.as_posix()} absent")
    if not chemin_reporting.is_file():
        erreurs.append(f"{chemin_reporting.as_posix()} absent")
    if erreurs:
        conclure(erreurs)

    chiffres = json.loads(chemin_chiffres.read_text(encoding="utf-8"))
    villes_calculees = [v.get("ville") for v in chiffres.get("villes", [])]
    if sorted(villes_calculees) != sorted(VILLES):
        erreurs.append("chiffres.json ne couvre pas les 7 villes")
    autorises = valeurs(chiffres)

    slides = decouper(chemin_reporting.read_text(encoding="utf-8"), erreurs)
    if slides and len(slides) != NB_SLIDES:
        erreurs.append(f"{len(slides)} slides au lieu de {NB_SLIDES}")

    if len(slides) >= 2:
        manquantes = [v for v in VILLES if not re.search(rf"\b{v}\b", slides[1])]
        if manquantes:
            erreurs.append("slide 2 : villes absentes : " + ", ".join(manquantes))

    for rang, slide in enumerate(slides, start=1):
        for jeton in NOMBRE.findall(COMMENTAIRE.sub("", slide)):
            propre = re.sub(r"[ \u00a0\u202f]", "", jeton).replace(",", ".")
            if round(float(propre), 2) not in autorises:
                lisible = re.sub(r"[\u00a0\u202f]", " ", jeton)
                erreurs.append(f"slide {rang} : chiffre absent de chiffres.json : {lisible}")

    conclure(erreurs)


def conclure(erreurs):
    for erreur in dict.fromkeys(erreurs):
        print(f"ERREUR: {erreur}")
    print("VERIFICATION: ECHEC" if erreurs else "VERIFICATION: OK")
    sys.exit(2 if erreurs else 0)


if __name__ == "__main__":
    main()
