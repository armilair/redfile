"""Vérifie docs/actions-playwright.yml. Exit 0 si la trace est complète, exit 2 sinon."""
import sys
from pathlib import Path


def echec(ligne):
    print(ligne, file=sys.stderr)
    print("VERDICT: INCOMPLET", file=sys.stderr)
    sys.exit(2)


def racine():
    ici = Path.cwd()
    if (ici / "app.py").is_file():
        return ici
    for dossier in Path(__file__).resolve().parents:
        if (dossier / "app.py").is_file():
            return dossier
    return None


def lire_actions(texte):
    blocs = []
    courant = None
    for brut in texte.splitlines():
        ligne = brut.strip()
        if ligne.startswith("- "):
            if courant:
                blocs.append(courant)
            courant = {}
            ligne = ligne[2:].strip()
        if courant is None or ":" not in ligne:
            continue
        cle, _, valeur = ligne.partition(":")
        courant[cle.strip()] = valeur.strip()
    if courant:
        blocs.append(courant)
    return blocs


def main():
    depot = racine()
    if depot is None:
        echec("app.py introuvable. Lancer le script depuis la racine du depot.")

    skill = Path(__file__).resolve().parent.parent
    champs = [
        ligne.strip()
        for ligne in (skill / "assets" / "champs.txt").read_text(encoding="utf-8").splitlines()
        if ligne.strip()
    ]
    outils = {
        ligne.strip()
        for ligne in (skill / "assets" / "outils.txt").read_text(encoding="utf-8").splitlines()
        if ligne.strip()
    }

    fichier = depot / "docs" / "actions-playwright.yml"
    if not fichier.is_file():
        echec("docs/actions-playwright.yml absent.")

    blocs = lire_actions(fichier.read_text(encoding="utf-8"))
    if not blocs:
        echec("aucune action dans le fichier.")

    for numero, bloc in enumerate(blocs, start=1):
        for champ in champs:
            if not bloc.get(champ):
                echec(f"action {numero}: {champ} manquant.")
        if bloc["outil"] not in outils:
            echec(f"action {numero}: outil inconnu.")
        horodatage = bloc["horodatage"]
        if len(horodatage) < 16 or horodatage[4] != "-" or horodatage[7] != "-" or horodatage[10] != "T":
            echec(f"action {numero}: horodatage attendu AAAA-MM-JJTHH:MM.")
        if "000" in bloc["constat"] and "€" in bloc["constat"]:
            echec(f"action {numero}: prix de bien dans le constat.")

    print(f"VERDICT: COMPLET ({len(blocs)} actions)")
    sys.exit(0)


if __name__ == "__main__":
    main()