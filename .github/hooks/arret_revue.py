"""Contrôle d'arrêt de la revue hebdo, pour Claude Code et Copilot CLI. Exit 0 dans tous les cas.

Arrêt du checker-revue : enregistre son verdict dans controle.json.
Arrêt de l'agent : bloque tant que le vérificateur n'est pas OK et que le checker
n'a pas dit PRET sur la version actuelle de la revue. Au 3e refus : ESCALADE.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PLAFOND = 3
CHECKER = "checker-revue"
VERIFICATEURS = [Path(".claude/skills/revue-hebdo/scripts/verifier_revue.py"),
                 Path(".github/skills/revue-hebdo/scripts/verifier_revue.py")]


def revue_en_cours(depot):
    """Dernière semaine calculée, si sa revue n'est ni livrée ni escaladée."""
    dossiers = sorted(p.parent for p in (depot / "revue").glob("semaine_*/chiffres.json"))
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
    fichier = dossier / "revue.md"
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
    verificateur = next((depot / v for v in VERIFICATEURS if (depot / v).exists()), depot / VERIFICATEURS[0])
    essai = subprocess.run(
        [sys.executable, str(verificateur), str(dossier)],
        cwd=depot, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if essai.returncode != 0:
        raisons.append("Verificateur en echec :\n" + essai.stdout.strip())
    if etat["verdict"] != "PRET":
        raisons.append(f"Checker : verdict {etat['verdict'] or 'absent'}. "
                       f"Fais relire la revue par l'agent {CHECKER}.\n{etat['motifs']}")
    elif etat["empreinte"] != empreinte(dossier):
        raisons.append(f"La revue a change depuis la derniere relecture : fais-la relire par {CHECKER}.")

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
        message = (f"ESCALADE : revue {semaine} refusee {PLAFOND} fois. Un humain reprend la main. "
                   f"Raisons dans revue/{semaine}/controle.json.")
        print(json.dumps({"systemMessage": message}, ensure_ascii=True))
        return

    ecrire(dossier, etat)
    raison = (f"Revue {semaine} refusee ({etat['refus']}/{PLAFOND}). "
              "Corrige revue.md, ne relance pas evaluer_revue.py.\n" + "\n".join(raisons))
    print(json.dumps({"decision": "block", "reason": raison}, ensure_ascii=True))


def main():
    brut = sys.stdin.read()
    try:
        donnees = json.loads(brut) if brut.strip() else {}
    except json.JSONDecodeError:
        donnees = {}
    depot = Path(os.environ.get("CLAUDE_PROJECT_DIR") or donnees.get("cwd") or os.getcwd())
    dossier, etat = revue_en_cours(depot)
    if dossier is None:
        sys.exit(0)

    # Claude Code, et Copilot CLI avec des événements en PascalCase : hook_event_name, noms en snake_case.
    # Copilot CLI avec des événements en camelCase : pas de hook_event_name, noms en camelCase.
    evenement = donnees.get("hook_event_name", "")
    noms = {donnees.get(cle) for cle in ("agent_type", "agent_name", "agentType", "agentName")}
    if evenement == "SubagentStop" or (not evenement and "agentName" in donnees):
        if CHECKER in noms:
            noter_verdict(donnees, dossier, etat)
    elif evenement == "Stop" or (not evenement and "stop_hook_active" in donnees):
        juger(depot, dossier, etat)
    sys.exit(0)


if __name__ == "__main__":
    main()
