---
name: revue-hebdo
description: Rédige la revue hebdomadaire des conversations du redfilebot pour l'équipe produit. À lancer seulement avec /revue-hebdo.
disable-model-invocation: true
---

Tu rédiges la revue de la semaine. Un script calcule, tu mets en mots, un vérificateur et un checker jugent, un humain décide.

1. Lance une seule fois `python .github/skills/revue-hebdo/scripts/evaluer_revue.py`. Il affiche le dossier `revue/semaine_NN` et y écrit `chiffres.json`. S'il affiche « Aucune semaine a traiter », arrête-toi et dis-le.
2. Lis `chiffres.json`. Écris `revue/semaine_NN/revue.md` : un titre `#`, puis ces cinq parties, dans cet ordre : `## Synthèse`, `## Conversion`, `## Règles du bot`, `## Pour l'équipe produit`, `## Décision attendue`.
3. Chaque conversation de `chiffres.json` est citée par son id. Les chiffres sont recopiés, aucun n'est calculé. Jamais le tarif 49,99 €. Aucune cause, aucune tendance. La décision reste une question posée à l'équipe produit.
4. Lance `python .github/skills/revue-hebdo/scripts/verifier_revue.py revue/semaine_NN`. Corrige la revue jusqu'à `VERIFICATION: OK`.
5. Fais relire la revue par l'agent `checker-revue`, en lui donnant le dossier, et attends sa réponse. `NON_PRET` : corrige, puis refais relire.
6. Conclus en une phrase : le contrôle d'arrêt décide. S'il te renvoie, corrige la revue selon sa raison et reprends à l'étape 4.

Ne modifie ni `chiffres.json`, ni `controle.json`, ni `redfilebot/`, ni le vérificateur, ni les hooks.
