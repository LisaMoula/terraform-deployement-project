# Scénario de démo live (soutenance)

Objectif : modifier l'infrastructure en direct via une Pull Request et montrer
le déclenchement de la CI/CD de bout en bout.

## Changement choisi

Redimensionner le plan App Service : `app_service_sku` **B1 → B2**.
Changement d'infra visible dans le `terraform plan` et dans le portail Azure.

Fichier : `terraform/terraform.tfvars` (ou variable `app_service_sku`).

## Pré-requis (avant la soutenance)

- App déployée et joignable : https://app-weather-dev-4e95s.azurewebsites.net
- `az login` fait, secrets GitHub en place, CI/CD vertes.
- Portail Azure ouvert sur le resource group `rg-weather-dev`.

## Déroulé (≈ 8 min)

### 1. Montrer l'existant (1 min)
- App Streamlit live (graphes météo, bandeau « ADLS gold container »).
- Portail : App Service `app-weather-dev-4e95s`, plan **B1**.

### 2. Créer la branche + la PR (2 min)
```bash
git checkout -b feature/modif-app-sku
# éditer terraform/variables.tf : default de app_service_sku -> "B2"
git commit -am "modif: app service plan B1 -> B2"
git push -u origin feature/modif-app-sku
gh pr create --base main --title "modif: app sku B2" --body "Resize plan"
```

### 3. Montrer la CI (2 min)
- Onglet Actions : le workflow **CI** tourne sur la PR.
- Jobs : Python tests → static (fmt/validate/tfsec/checkov) → **plan**.
- Ouvrir le job **plan** : le diff montre `app_service_sku: "B1" -> "B2"`.
- Télécharger l'artefact **tfplan**.

### 4. Merger + déclencher la CD (2 min)
```bash
gh pr merge --merge
```
- Lancer la **CD** (workflow_dispatch) sur `main`.
- `deploy-dev` applique → plan App Service passe en **B2**.
- `deploy-prod` se met en **attente d'approbation** (gate manuel).
- Approuver → `deploy-prod` exécute `terraform apply`.

### 5. Vérifier le résultat (1 min)
- Portail : App Service plan = **B2**.
- App toujours joignable (HTTP 200).

```bash
az appservice plan show -g rg-weather-dev -n plan-weather-dev --query sku.name -o tsv
```

## Rollback (si besoin)

Repasser `app_service_sku` à `B1`, nouvelle PR, re-merge, re-apply.

## Points à souligner pendant la démo

- **IaC** : un seul changement de variable, tout le reste est reproductible.
- **Remote state + locking** : state partagé sur Azure Storage.
- **Sécurité** : aucun secret en clair, Key Vault + managed identity, auth CI/CD
  par Service Principal.
- **Gate prod** : séparation dev automatique / prod avec validation humaine.
