---
name: documenter-playwright-skill
description: Documente chaque action Playwright dans docs/actions-playwright.yml. À utiliser dès qu'on ouvre ou qu'on manipule le site redfile avec le navigateur.
---

À chaque appel Playwright, laisse une trace. Ne colle pas le snapshot dans le fichier, ni dans la réponse.

1. Le fichier est `docs/actions-playwright.yml`. S'il n'existe pas, crée-le avec une clé `actions:`.
2. Pour chaque action, ajoute une entrée : `outil`, `cible`, `constat`. Le constat tient en une phrase.
3. Si des entrées sont déjà là, garde-les. Ajoute après.
4. Le tarif 49,99 € peut être noté. N'écris aucun prix de bien.
5. Ne modifie pas `app.py`, `redfilebot/`, ni `README.md`.

Outils à noter tels quels : `browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, `browser_resize`, `browser_mouse_wheel`.
