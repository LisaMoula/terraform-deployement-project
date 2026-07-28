# Présentation (trame slides)

> Une slide par bloc. Objectif : ~12-15 slides, ~15 min + démo.

## Slide 1 — Titre
- Projet DevOps CI/CD & IaC — Application météo Big Data
- Nom, promo ESGI, date.

## Slide 2 — Contexte & objectifs
- Ingestion météo (Open-Meteo) → traitement → dashboard.
- 100 % Azure, IaC, sécurisé, automatisé.

## Slide 3 — Architecture (schéma)
- Open-Meteo → App Service (Streamlit) → ADLS Gen2 (landing/gold).
- Key Vault (secrets), ACR (image), remote state.

## Slide 4 — Application & données
- ETL : extract / transform / pipeline.
- Zones landing (brut) / gold (nettoyé).
- Dashboard Streamlit (KPIs, graphes, carte).

## Slide 5 — Conteneurisation
- Dockerfile slim, non-root, healthcheck.
- Image sur Azure Container Registry.

## Slide 6 — Infrastructure Terraform
- Modules : storage, keyvault, acr, app.
- Remote state + state locking.
- Variables / outputs.

## Slide 7 — Sécurité
- Zéro secret en clair.
- Key Vault + managed identity + Key Vault reference.
- Service Principal, rôles restreints.

## Slide 8 — CI
- Tests, fmt, validate, tfsec/checkov, plan + artefact.
- Capture : CI verte.

## Slide 9 — CD
- Dev auto → gate prod manuel → apply.
- Capture : job prod en attente d'approbation.

## Slide 10 — Gestion Git
- main / feature/add-* / feature/modif-*.
- Flux PR + revue.

## Slide 11 — Démo live
- Modifier `app_service_sku` B1 → B2 via PR.
- CI plan → merge → CD → gate → apply.
- Voir résultat dans le portail.

## Slide 12 — Bilan
- Ce qui marche, limites (prod = gate même stack, coût).
- Améliorations : env prod isolé, monitoring, scan image.

## Slide 13 — Questions
