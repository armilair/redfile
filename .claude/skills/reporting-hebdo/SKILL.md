---
name: reporting-hebdo
description: Rédige le reporting hebdomadaire de performance du modèle de prix, en 5 slides Marp, pour la première semaine de ventes non traitée. À lancer seulement avec /reporting-hebdo.
disable-model-invocation: true
---

Tu rédiges le reporting de la semaine. Un script calcule les chiffres, tu les mets en mots, un vérificateur et un checker jugent, un humain décide.

1. Lance une seule fois `python ${CLAUDE_SKILL_DIR}/scripts/evaluer_semaine.py`. Il affiche le dossier `reporting/semaine_NN` et y écrit `chiffres.json`. S'il affiche « Aucune semaine a traiter », arrête-toi et dis-le.
2. Lis `chiffres.json`. Écris `reporting/semaine_NN/reporting.md` au format Marp :
   - en-tête : `marp: true`, `theme: default`, `paginate: true`, `footer: Redfile · Performance du modèle de prix`, rien d'autre ;
   - exactement 5 slides, séparées par une ligne `---` précédée d'une ligne vide ;
   - slide 1, synthèse de la semaine ; slide 2, erreur par ville : un tableau des 7 villes (ventes, erreur absolue moyenne, erreur relative moyenne, écart au seuil) ; slide 3, villes à surveiller : `ville_la_plus_proche_du_seuil` ; slide 4, ce que cela change pour Redfile : l'écart moyen en euros par estimation, le prix étant la promesse du produit ; slide 5, décision humaine attendue : réentraîner ou non, la décision revient à un humain.
3. Tu choisis seulement les titres-messages et les phrases. Chaque chiffre est recopié de `chiffres.json`, au même arrondi : `21 143 €`, `4,8 %`, `5,2 points`. Aucun autre chiffre : pas de date, pas de liste numérotée, pas de tarif, pas de manque à gagner, pas de chiffre d'affaires. Aucune tendance, aucune cause, aucune direction de l'erreur. Aucune mention de formation, de démo ni de boucle.
4. Lance `python ${CLAUDE_SKILL_DIR}/scripts/verifier_reporting.py reporting/semaine_NN`. Corrige le reporting jusqu'à `VERIFICATION: OK`.
5. Fais relire le reporting par le sous-agent `checker-reporting`, en lui donnant le dossier.
6. Conclus en une phrase, quel que soit le verdict : c'est le contrôle d'arrêt qui décide. S'il te renvoie, corrige le reporting selon sa raison et reprends à l'étape 4.

Ne modifie ni `chiffres.json`, ni `controle.json`, ni `data/`, ni `model/`, ni le vérificateur, ni les hooks. Ne réentraîne jamais le modèle.
