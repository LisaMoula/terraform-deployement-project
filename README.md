# Weather DevOps Project

Ingest free weather data (Open-Meteo), clean it with pandas, visualize it in
Streamlit, containerize with Docker, and deploy to Azure with Terraform
(remote state + Key Vault).

## Layout

```
.
├── data/
│   ├── raw/            # raw JSON payloads from the API
│   └── processed/      # cleaned CSV
├── src/
│   ├── extract.py      # call Open-Meteo -> raw JSON
│   ├── transform.py    # pandas cleaning -> CSV
│   └── pipeline.py     # ETL orchestration
├── tests/
│   ├── test_extract.py
│   └── test_transform.py
├── app.py              # Streamlit dashboard
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── scripts/            # Azure backend bootstrap
└── terraform/          # infrastructure as code
```

## Local run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m src.pipeline          # ETL: fetch, clean, write CSV
pytest -v                       # tests (HTTP mocked)
streamlit run app.py            # dashboard on http://localhost:8501
```

Custom location: `python -m src.pipeline --lat 45.75 --lon 4.85 --days 5`

## Docker

```powershell
docker compose up --build       # http://localhost:8501
```

## Terraform (Azure)

```
terraform/
├── main.tf providers.tf backend.tf variables.tf outputs.tf
├── terraform.tfvars.example
└── modules/
    ├── storage/    # Data Lake Gen2 + landing/gold containers
    ├── keyvault/   # Key Vault + access policies + secrets
    └── app/        # App Service Linux (Streamlit container) + managed identity
```

Resources: Resource Group, Storage Account (Data Lake), Key Vault, App Service.
State is stored remotely on an Azure Storage Account with state locking.

```powershell
az login
./scripts/bootstrap_backend.ps1              # creates backend, writes backend.hcl

cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init -backend-config=backend.hcl
terraform plan -out=tfplan
terraform apply tfplan
```

## CI (GitHub Actions)

`.github/workflows/ci.yml` runs on push to `feature/**` and PRs to `main`:

1. Python tests (`pytest`).
2. `terraform fmt -check` and `terraform validate`.
3. Security scan (`tfsec` + `checkov`, soft fail).
4. `terraform plan` and upload the `tfplan` artifact.

Azure auth uses OIDC (no client secret). One-time setup creates the service
principal and pushes the repo secrets:

```powershell
az login
gh auth login
./scripts/setup_github_oidc.ps1
```

Repo secrets used: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`,
`TFSTATE_RG`, `TFSTATE_SA`, `TFSTATE_CONTAINER`.

## CD (GitHub Actions)

`.github/workflows/cd.yml` runs on `workflow_dispatch` or a published release:

1. `deploy-dev` (environment `dev`, auto): terraform apply, build/push the image
   to ACR, restart the App Service.
2. `deploy-prod` (environment `prod`, **manual approval gate**): re-applies the
   validated plan after a required reviewer approves.

Azure auth uses a service principal (secret `AZURE_CREDENTIALS`, the JSON from
`az ad sp create-for-rbac --json-auth`). The GitHub `prod` environment has a
required reviewer (created by `scripts/setup_cd.ps1`).

## Security

No secrets in the repo. The storage connection string lives in Key Vault; the
App Service reads it at runtime through a Key Vault reference
(`@Microsoft.KeyVault(SecretUri=...)`) resolved by its system-assigned managed
identity. `backend.hcl`, `*.tfvars`, and `*.tfstate` are gitignored.

## Docs

- [docs/DEMO.md](docs/DEMO.md) - live demo runbook (infra change via PR).
- [docs/DOSSIER_TECHNIQUE.md](docs/DOSSIER_TECHNIQUE.md) - technical report outline.
- [docs/PRESENTATION.md](docs/PRESENTATION.md) - slides outline.

## Data source

[Open-Meteo](https://open-meteo.com/) - free weather API, no API key.

## Git branches

- `main` - stable branch.
- `feature/add-*` - new feature.
- `feature/modif-*` - change to existing code.
