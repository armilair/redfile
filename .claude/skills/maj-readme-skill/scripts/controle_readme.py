"""Vérifie que le README cite chaque ligne de assets/faits.txt. Exit 0 ou 2."""
import sys
from pathlib import Path


def racine():
    ici = Path.cwd()
    if (ici / "README.md").is_file() and (ici / "app.py").is_file():
        return ici
    for dossier in Path(__file__).resolve().parents:
        if (dossier / "README.md").is_file() and (dossier / "app.py").is_file():
            return dossier
    return None


def main():
    depot = racine()
    if depot is None:
        print("README.md introuvable.", file=sys.stderr)
        sys.exit(2)
    faits = Path(__file__).resolve().parent.parent / "assets" / "faits.txt"
    lignes = [
        ligne.strip()
        for ligne in faits.read_text(encoding="utf-8").splitlines()
        if ligne.strip()
    ]
    readme = (depot / "README.md").read_text(encoding="utf-8")
    for ligne in lignes:
        if ligne not in readme:
            print(f"MANQUE: {ligne}", file=sys.stderr)
            print("VERDICT: README EN RETARD", file=sys.stderr)
            sys.exit(2)
    print("VERDICT: README A JOUR")
    sys.exit(0)


if __name__ == "__main__":
    main()
