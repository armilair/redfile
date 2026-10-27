"""Calcule les chiffres de la revue des conversations d'une semaine. Exit 0, ou 1 s'il n'y a rien à traiter.

Sans argument : la première semaine de redfilebot/logs/ sans revue/semaine_NN/chiffres.json.
Avec un fichier .jsonl en argument : ce fichier, chiffres écrits dans revue/<nom du fichier>/.

Un prix de logement s'écrit avec une espace entre les milliers, suivi de € : « 536 147 € ».
« 49,99 € TTC » est le tarif de l'estimation : ce n'est pas un prix de logement.
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[4]
PRIX = re.compile(r"(\d{1,3}(?:[ \u00a0\u202f]\d{3})+)\s*€")
ETAPES = ["fiche_complete", "paiement", "rdv_propose", "rdv_accepte"]


def fichier_a_traiter():
    if len(sys.argv) > 1:
        return Path(sys.argv[1])
    for chemin in sorted((RACINE / "redfilebot" / "logs").glob("semaine_*.jsonl")):
        if not (RACINE / "revue" / chemin.stem / "chiffres.json").exists():
            return chemin
    return None


def prix_cites(texte):
    return [int(re.sub(r"\D", "", trouve)) for trouve in PRIX.findall(texte)]


def controler(conversation):
    """Règles du bot : le prix cité est montant_xgboost, aucun prix avant le paiement."""
    messages = conversation["messages"]
    paiement = next((i for i, m in enumerate(messages)
                     if m["role"] == "client" and "49,99" in m["texte"]), None)
    cites, avant_paiement = [], False
    for i, message in enumerate(messages):
        if message["role"] != "bot":
            continue
        trouves = prix_cites(message["texte"])
        cites += trouves
        if trouves and (not conversation["paiement"] or paiement is None or i < paiement):
            avant_paiement = True
    attendu = conversation["montant_xgboost"]
    if conversation["paiement"]:
        prix_exact = bool(cites) and all(prix == attendu for prix in cites)
    else:
        prix_exact = not cites
    return {
        "id": conversation["id"],
        **{etape: bool(conversation[etape]) for etape in ETAPES},
        "montant_xgboost": attendu,
        "prix_cites": cites,
        "prix_exact": prix_exact,
        "prix_avant_paiement": avant_paiement,
        "conforme": prix_exact and not avant_paiement,
    }


def main():
    chemin = fichier_a_traiter()
    if chemin is None:
        print("Aucune semaine a traiter.")
        sys.exit(1)

    lignes = chemin.read_text(encoding="utf-8").splitlines()
    conversations = [controler(json.loads(ligne)) for ligne in lignes if ligne.strip()]
    total = len(conversations)
    nombres = {etape: sum(c[etape] for c in conversations) for etape in ETAPES}
    conformes = sum(c["conforme"] for c in conversations)
    numero = re.search(r"(\d+)$", chemin.stem)

    chiffres = {
        "semaine": chemin.stem,
        "numero_semaine": int(numero.group(1)) if numero else 0,
        "nb_conversations": total,
        "conversion": nombres,
        "taux_pct": {etape: round(100 * n / total, 1) for etape, n in nombres.items()},
        "regles": {
            "conversations_conformes": conformes,
            "taux_conformes_pct": round(100 * conformes / total, 1),
            "prix_inexacts": sum(not c["prix_exact"] for c in conversations),
            "prix_avant_paiement": sum(c["prix_avant_paiement"] for c in conversations),
        },
        "conversations": conversations,
    }

    dossier = RACINE / "revue" / chemin.stem
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "chiffres.json").write_text(
        json.dumps(chiffres, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"revue/{chemin.stem}")


if __name__ == "__main__":
    main()
