#!/usr/bin/env bash
# Creates the Terraform remote state backend (RG + Storage Account + Container).
# Run once before the first terraform init.
#
#   az login
#   ./scripts/bootstrap_backend.sh
set -euo pipefail

LOCATION="France Central"
RG_NAME="rg-tfstate-weather"
CONTAINER_NAME="tfstate"
SUFFIX=$(printf "%04d" $((RANDOM % 10000)))
STORAGE_NAME="sttfstateweather${SUFFIX}"

az group create --name "${RG_NAME}" --location "${LOCATION}" --output none

az storage account create \
  --name "${STORAGE_NAME}" \
  --resource-group "${RG_NAME}" \
  --location "${LOCATION}" \
  --sku Standard_LRS \
  --encryption-services blob \
  --min-tls-version TLS1_2 \
  --allow-blob-public-access false \
  --output none

az storage container create \
  --name "${CONTAINER_NAME}" \
  --account-name "${STORAGE_NAME}" \
  --auth-mode login \
  --output none

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat > "${SCRIPT_DIR}/../terraform/backend.hcl" <<EOF
resource_group_name  = "${RG_NAME}"
storage_account_name = "${STORAGE_NAME}"
container_name       = "${CONTAINER_NAME}"
key                  = "weather.dev.tfstate"
EOF

echo "Backend ready. Generated terraform/backend.hcl"
echo "Next: cd terraform && terraform init -backend-config=backend.hcl"
