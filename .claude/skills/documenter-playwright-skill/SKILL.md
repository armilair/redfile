---
name: documenter-playwright-skill
description: Documente chaque action Playwright dans docs/actions-playwright.yml, avec un horodatage, puis vérifie le fichier. À utiliser dès qu'on ouvre ou qu'on manipule le site redfile avec le navigateur.
---

À chaque appel Playwright, laisse une trace dans `docs/actions-playwright.yml` conforme à la procédure ci-dessous. Ne crée aucun autre fichier. Ne colle pas le snapshot dans le YAML, ni dans la réponse, ni ailleurs.

1. Le fichier est `docs/actions-playwright.yml`. S'il n'existe pas, crée-le avec une clé `actions:`. Le modèle d'une entrée est `assets/exemple.yml`. Les champs obligatoires sont ceux de `assets/champs.txt`.
2. Pour chaque action, ajoute une entrée. Le constat tient en une phrase. L'horodatage est écrit par toi, au format `AAAA-MM-JJTHH:MM`, heure de l'action.
3. Si des entrées sont déjà là, garde-les. Ajoute après.
4. Le tarif 49,99 € peut être noté. N'écris aucun prix de bien.
5. Lance `python ${CLAUDE_SKILL_DIR}/scripts/controle_trace.py`. Code 2 : complète le YAML, puis relance le script. Ne modifie ni le script, ni les assets, pour faire taire le verdict.
6. Le seul fichier que tu peux créer ou modifier est `docs/actions-playwright.yml`. Ne modifie pas `app.py`, `redfilebot/`, ni `README.md`.

Outils à noter tels quels : ceux de `assets/outils.txt`.
