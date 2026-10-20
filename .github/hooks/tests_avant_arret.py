"""Hook d'arrêt : pas de conclusion tant que pytest est rouge. Exit 0 dans tous les cas."""
import json
import os
import subprocess
import sys


def texte(blob):
    if not blob:
        return ""
    if isinstance(blob, str):
        return blob
    try:
        return blob.decode("utf-8")
    except UnicodeDecodeError:
        return blob.decode("cp1252", errors="replace")


def main():
    brut = sys.stdin.read()
    try:
        donnees = json.loads(brut) if brut.strip() else {}
    except json.JSONDecodeError:
        donnees = {}
    if donnees.get("stop_hook_active"):
        sys.exit(0)
    racine = donnees.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        essai = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-x"],
            cwd=racine,
            capture_output=True,
        )
    except OSError as erreur:
        raison = "Tests en echec : corrige avant de conclure.\n" + str(erreur)
    else:
        if essai.returncode == 0:
            sys.exit(0)
        sortie = (texte(essai.stdout) + texte(essai.stderr)).strip()
        fin = "\n".join(sortie.splitlines()[-15:])
        raison = "Tests en echec : corrige avant de conclure.\n" + fin
    # ASCII seul : sous Windows la sortie du hook est en cp1252.
    print(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=True))
    sys.exit(0)


if __name__ == "__main__":
    main()
