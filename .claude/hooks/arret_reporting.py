"""Contrôle d'arrêt du reporting hebdo. Exit 0 dans tous les cas.

SubagentStop (checker-reporting) : enregistre son verdict dans controle.json.
Stop : bloque tant que le vérificateur n'est pas OK et que le checker n'a pas
dit PRET sur la version actuelle du reporting. Au 3e refus : ESCALADE, la main
passe à un humain.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PLAFOND = 3
CHECKER = "checker-reporting"
VERIFICATEUR = Path(".claude/skills/reporting-hebdo/scripts/verifier_reporting.py")


def reporting_en_cours(depot):
    """Dernière semaine calculée, si son reporting n'est ni livré ni escaladé."""
    dossiers = sorted(p.parent for p in (depot / "reporting").glob("semaine_*/chiffres.json"))
    if not dossiers:
        return None, None
    dossier = dossiers[-1]
    chemin = dossier / "controle.json"
    if chemin.exists():
        etat = json.loads(chemin.read_text(encoding="utf-8"))
    else:
        etat = {"semaine": dossier.name, "statut": "EN_COURS", "refus": 0,
                "verdict": None, "empreinte": None, "motifs": "", "raisons": []}
    if etat["statut"] != "EN_COURS":
        return None, None
    return dossier, etat


def ecrire(dossier, etat):
    (dossier / "controle.json").write_text(
        json.dumps(etat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def empreinte(dossier):
    fichier = dossier / "reporting.md"
    return hashlib.sha256(fichier.read_bytes()).hexdigest() if fichier.exists() else None


def noter_verdict(donnees, dossier, etat):
    message = donnees.get("last_assistant_message") or donnees.get("response") or ""
    trouves = re.findall(r"VERDICT\s*:\s*(NON_PRET|PRET)", message)
    etat["verdict"] = trouves[-1] if trouves else "ILLISIBLE"
    etat["empreinte"] = empreinte(dossier)
    etat["motifs"] = message.strip()[-1500:]
    ecrire(dossier, etat)


def juger(depot, dossier, etat):
    raisons = []
    essai = subprocess.run(
        [sys.executable, str(depot / VERIFICATEUR), str(dossier)],
        cwd=depot, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if essai.returncode != 0:
        raisons.append("Verificateur en echec :\n" + essai.stdout.strip())
    if etat["verdict"] != "PRET":
        raisons.append(f"Checker : verdict {etat['verdict'] or 'absent'}. "
                       f"Fais relire le reporting par le sous-agent {CHECKER}.\n{etat['motifs']}")
    elif etat["empreinte"] != empreinte(dossier):
        raisons.append(f"Le reporting a change depuis la derniere relecture : fais-le relire par {CHECKER}.")

    if not raisons:
        etat["statut"] = "LIVRE"
        ecrire(dossier, etat)
        return

    etat["refus"] += 1
    etat["raisons"] = raisons
    semaine = dossier.name
    if etat["refus"] >= PLAFOND:
        etat["statut"] = "ESCALADE"
        ecrire(dossier, etat)
        message = (f"ESCALADE : reporting {semaine} refuse {PLAFOND} fois. Un humain reprend la main. "
                   f"Raisons dans reporting/{semaine}/controle.json.")
        print(json.dumps({"systemMessage": message}, ensure_ascii=True))
        return

    ecrire(dossier, etat)
    raison = (f"Reporting {semaine} refuse ({etat['refus']}/{PLAFOND}). "
              "Corrige reporting.md, ne relance pas evaluer_semaine.py.\n" + "\n".join(raisons))
    # ASCII seul : sous Windows la sortie du hook est en cp1252.
    print(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=True))


def main():
    brut = sys.stdin.read()
    try:
        donnees = json.loads(brut) if brut.strip() else {}
    except json.JSONDecodeError:
        donnees = {}
    depot = Path(os.environ.get("CLAUDE_PROJECT_DIR") or donnees.get("cwd") or os.getcwd())
    dossier, etat = reporting_en_cours(depot)
    if dossier is None:
        sys.exit(0)

    evenement = donnees.get("hook_event_name") or ""
    nom = (donnees.get("agent_type") or donnees.get("agent_name")
           or donnees.get("agentType") or donnees.get("agentName") or "")
    # Claude envoie Stop et SubagentStop. Copilot CLI envoie les mêmes noms
    # si le fichier de hooks les écrit en PascalCase, sinon agentStop et subagentStop.
    if evenement in ("SubagentStop", "subagentStop") or (not evenement and nom):
        if nom == CHECKER:
            noter_verdict(donnees, dossier, etat)
    elif evenement in ("Stop", "agentStop") or (not evenement and "stop_hook_active" in donnees):
        juger(depot, dossier, etat)
    sys.exit(0)


if __name__ == "__main__":
    main()