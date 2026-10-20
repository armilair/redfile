"""Tests métier redfile : le prix du bien vient du modèle, le tarif vient de la constante."""
import re
from pathlib import Path

import pytest

import app as redfile

RACINE = Path(__file__).resolve().parent.parent

FICHE = {
    "surface": 53.1, "type_bien": "appartement", "nb_pieces": 3, "nb_chambres": 2,
    "nb_salles_de_bain": 1, "etage": 6, "annee_construction": 2001, "ville": "Bordeaux",
    "etat": "excellent", "dpe": "E", "garage": "non", "ascenseur": "oui",
    "balcon_terrasse": "non", "cave": "non", "distance_centre": 3.9,
}


class FauxModele:
    """Remplace XGBoost : renvoie une valeur reconnaissable et compte les appels."""

    def __init__(self):
        self.appels = 0

    def predict(self, tableau):
        self.appels += 1
        return [123456.0]


@pytest.fixture
def client():
    redfile.app.config["TESTING"] = True
    return redfile.app.test_client()


def test_estimer_prix_passe_par_predict(monkeypatch):
    faux = FauxModele()
    monkeypatch.setattr(redfile, "MODELE", faux)
    assert redfile.estimer_prix(FICHE) == 123456
    assert faux.appels == 1


def test_le_tarif_s_affiche_via_la_constante(monkeypatch, client):
    monkeypatch.setattr(redfile, "PRIX_ESTIMATION_TTC", 59.5)
    for page in ("/", "/estimation"):
        assert "59,50" in client.get(page).get_data(as_text=True)


def test_aucun_prix_de_bien_ecrit_en_dur():
    # Un montant de bien : au moins quatre chiffres groupés, suivis de « € » (ex. « 280 000 € »)
    montant = re.compile(r"\d{1,3}(?:[  .]\d{3})+\s*€|\d{4,}\s*€")
    fichiers = [RACINE / "app.py", *(RACINE / "redfilebot").glob("*.py"),
                *(RACINE / "website" / "templates").glob("*.html")]
    fautifs = [f"{f.relative_to(RACINE)} : {m.group(0)}"
               for f in fichiers
               for m in montant.finditer(f.read_text(encoding="utf-8"))]
    assert not fautifs, "Prix de bien écrit en dur : " + ", ".join(fautifs)