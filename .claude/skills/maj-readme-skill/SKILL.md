---
name: maj-readme-skill
description: Met à jour les sections Lancer et Le dépôt du README.md à partir du code. À utiliser seulement quand on tape /maj-readme-skill.
disable-model-invocation: true
---

Remets `README.md` au niveau du code. Ne touche que les sections « Lancer » et « Le dépôt ».

1. Lis `requirements.txt`, le début de `model/train_model.py`, et le démarrage de `app.py`.
2. Lis `assets/faits.txt`. Chaque ligne doit rester dans le README. N'invente pas une commande qui n'est pas dans ce fichier, ni dans les trois fichiers de code.
3. Réécris ces deux sections pour qu'elles disent ce que ces fichiers disent : les commandes de lancement, le port, les dossiers et leur rôle.
4. Lance `python ${CLAUDE_SKILL_DIR}/scripts/controle_readme.py`. Code 2 : une ligne de `assets/faits.txt` manque dans le README. Corrige le README. Ne modifie pas `assets/faits.txt` ni le script pour faire taire le verdict.
5. Le tarif 49,99 € TTC peut rester. N'écris aucun prix de bien. N'ouvre pas `model/model.joblib`. N'appelle pas `estimer_prix`.

Si le README est déjà juste, dis-le. Ne le réécris pas pour le principe.
