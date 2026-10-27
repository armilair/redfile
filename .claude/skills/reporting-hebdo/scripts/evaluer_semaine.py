"""Calcule les chiffres de la première semaine de ventes non traitée. Exit 0, ou 1 s'il n'y a rien à traiter."""
import json
import sys
from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RACINE))

from app import estimer_prix, valider  # noqa: E402

SEUIL_PCT = 10
VILLES = ["Paris", "Lyon", "Lille", "Marseille", "Rennes", "Bordeaux", "Strasbourg"]
CHAMPS = [
    "surface", "type_bien", "nb_pieces", "nb_chambres", "nb_salles_de_bain",
    "etage", "annee_construction", "ville", "etat", "dpe", "garage",
    "ascenseur", "balcon_terrasse", "cave", "distance_centre",
]


def semaine_a_traiter():
    for csv in sorted((RACINE / "data" / "ventes").glob("semaine_*.csv")):
        if not (RACINE / "reporting" / csv.stem / "chiffres.json").exists():
            return csv
    return None


def mesurer(ventes):
    erreur = (ventes["prix"] - ventes["predit"]).abs()
    relative = round(float((erreur / ventes["prix"]).mean() * 100), 1)
    return {
        "ventes": int(len(ventes)),
        "erreur_absolue_moyenne_eur": int(round(float(erreur.mean()))),
        "erreur_relative_moyenne_pct": relative,
        "ecart_au_seuil_pts": round(SEUIL_PCT - relative, 1),
    }


def main():
    csv = semaine_a_traiter()
    if csv is None:
        print("Aucune semaine a traiter.")
        sys.exit(1)

    ventes = pd.read_csv(csv)
    fiches = ventes[CHAMPS].to_dict("records")
    ventes["predit"] = [estimer_prix(valider(fiche)) for fiche in fiches]

    villes = []
    for ville in VILLES:
        mesure = mesurer(ventes[ventes["ville"] == ville])
        mesure["alerte"] = mesure["erreur_relative_moyenne_pct"] > SEUIL_PCT
        villes.append({"ville": ville, **mesure})

    chiffres = {
        "semaine": csv.stem,
        "numero_semaine": int(csv.stem.split("_")[1]),
        "seuil_alerte_pct": SEUIL_PCT,
        "nb_villes": len(VILLES),
        "nb_villes_en_alerte": sum(v["alerte"] for v in villes),
        "global": mesurer(ventes),
        "villes": villes,
        "ville_la_plus_proche_du_seuil": min(villes, key=lambda v: v["ecart_au_seuil_pts"])["ville"],
    }

    dossier = RACINE / "reporting" / csv.stem
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "chiffres.json").write_text(
        json.dumps(chiffres, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"reporting/{csv.stem}")


if __name__ == "__main__":
    main()
