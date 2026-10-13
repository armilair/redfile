---
paths:
  - "website/templates/**"
  - "website/static/**"
---

# Interface d'estimation

- Le client décrit le bien avec ses mots. L'Interface collecte les 15 caractéristiques.
- Une information absente reste null et devient une question dans la conversation.
- L'interface ne calcule ni n'affiche aucun prix de bien. Le montant du bien est celui que renvoie POST /estimate, après le paiement simulé.
- 49,99 € est le tarif du service, déjà connu. Il peut rester affiché.
- On réutilise l'en-tête, le pied de page et styles.css. On ne réécrit pas la charte.