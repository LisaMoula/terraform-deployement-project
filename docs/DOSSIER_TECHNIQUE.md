# Dossier technique — Projet DevOps CI/CD & IaC


## 1. Contexte et objectifs

- Application Big Data météo : ingestion Open-Meteo → traitement pandas →
  visualisation Streamlit.
- Déploiement 100 % Azure via Terraform (IaC), sécurisé (Key Vault), automatisé
  (CI/CD GitHub Actions).

## 2. Architecture

- Schéma d'architecture (à insérer) : Open-Meteo → App Service (conteneur
  Streamlit) → ADLS Gen2 (landing/gold) ; secrets dans Key Vault ; image dans ACR.
- Flux de données : `src/extract.py` → `src/transform.py` → `src/pipeline.py`.
- Zones data : container `landing` (JSON brut), `gold` (CSV nettoyé).

## 3. Application

- Extraction : API Open-Meteo, sans clé (`src/extract.py`).
- Transformation : nettoyage/typage pandas (`src/transform.py`).
- Stockage : ADLS quand `STORAGE_CONNECTION_STRING` présent, sinon local
  (`src/storage.py`).
- Dashboard : `app.py` (KPIs, graphes, carte).
- Tests : `tests/` (pytest, HTTP mické).

## 4. Conteneurisation

- `Dockerfile` : `python:3.11-slim`, utilisateur non-root, healthcheck.
- `docker-compose.yml` : port 8501, volume `data`.
- Image publiée sur Azure Container Registry.

## 5. Infrastructure as Code (Terraform)

- Structure : `providers.tf`, `backend.tf`, `variables.tf`, `outputs.tf`,
  `main.tf` + modules.
- Modules : `storage` (Data Lake), `keyvault`, `acr`, `app` (App Service).
- Remote state : Azure Storage Account + state locking (blob lease).
- Ressources : Resource Group, Storage/ADLS, Key Vault, ACR, App Service Linux.

## 6. Sécurité

- Aucun secret en clair (gitignore : `backend.hcl`, `*.tfvars`, `*.tfstate`).
- Key Vault : secret `storage-connection-string`.
- App Service : managed identity (SystemAssigned) → lecture du secret via
  Key Vault reference `@Microsoft.KeyVault(...)`.
- Pull image ACR par managed identity (rôle AcrPull).
- Auth CI/CD : Service Principal (OIDC pour la CI, `AZURE_CREDENTIALS` pour la CD),
  rôles restreints (Contributor sur le RG applicatif, Blob Data sur le tfstate).

## 7. CI (intégration continue)

- Fichier : `.github/workflows/ci.yml`.
- Étapes : tests Python, `terraform fmt`, `validate`, `tfsec`, `checkov`,
  `terraform plan` + artefact `tfplan`.
- Déclencheurs : push `feature/**`, PR vers `main`.

## 8. CD (déploiement continu)

- Fichier : `.github/workflows/cd.yml`.
- `deploy-dev` : apply automatique + build/push image + restart app.
- `deploy-prod` : **gate manuel** (environnement GitHub `prod`, reviewer requis)
  puis `terraform apply`.
- Déclencheurs : `workflow_dispatch`, `release`.

## 9. Gestion Git

- Branches : `main`, `feature/add-*`, `feature/modif-*`.
- PR + revue avant merge sur `main`.

## 10. Démonstration

- Voir `docs/DEMO.md` (scénario de modification live B1 → B2).

## 11. Bilan et améliorations

- Limites : prod = gate sur le même stack (pas de 2e environnement pour maîtriser
  le coût des crédits étudiants).
- Pistes : environnement prod isolé, tests d'intégration, monitoring/alerting,
  scan d'image conteneur, politique de branches protégées.

## Annexes

- URLs, IDs de ressources, captures d'écran (CI/CD vertes, portail Azure).
