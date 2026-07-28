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

## Security

No secrets in the repo. The storage connection string is written to Key Vault
and read back via `data "azurerm_key_vault_secret"`. The App Service uses a
system-assigned managed identity with read-only Key Vault access. `backend.hcl`,
`*.tfvars`, and `*.tfstate` are gitignored.

## Data source

[Open-Meteo](https://open-meteo.com/) - free weather API, no API key.

## Git branches

- `main` - stable branch.
- `feature/add-*` - new feature.
- `feature/modif-*` - change to existing code.
