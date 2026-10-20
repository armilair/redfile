"""Bloque l'entraînement. Exit 2 si la commande lance train_model.py, 0 sinon."""
import json
import sys


def main():
    brut = sys.stdin.read()
    donnees = json.loads(brut) if brut.strip() else {}
    entree = donnees.get("tool_input") or donnees.get("toolArgs") or {}
    if isinstance(entree, str):
        try:
            entree = json.loads(entree) if entree.strip() else {}
        except json.JSONDecodeError:
            entree = {}
    commande = str((entree or {}).get("command") or "")
    commande = commande.replace("\\", "/")
    if "train_model.py" in commande:
        motif = "Entrainement bloque. Le modele ne se reecrit pas sur cette branche."
        print(json.dumps({
            "permissionDecision": "deny",
            "permissionDecisionReason": motif,
        }, ensure_ascii=True))
        print(motif, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
