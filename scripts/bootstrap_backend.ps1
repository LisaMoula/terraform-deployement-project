<#
Creates the Terraform remote state backend (Resource Group + Storage Account +
Container). Run once before the first terraform init.

  az login
  ./scripts/bootstrap_backend.ps1
#>

$ErrorActionPreference = "Stop"

$Location      = "France Central"
$RgName        = "rg-tfstate-weather"
$ContainerName = "tfstate"
$Suffix        = -join ((0..3) | ForEach-Object { (Get-Random -Minimum 0 -Maximum 10) })
$StorageName   = "sttfstateweather$Suffix"

az group create --name $RgName --location $Location --output none

az storage account create `
  --name $StorageName `
  --resource-group $RgName `
  --location $Location `
  --sku Standard_LRS `
  --encryption-services blob `
  --min-tls-version TLS1_2 `
  --allow-blob-public-access false `
  --output none

az storage container create `
  --name $ContainerName `
  --account-name $StorageName `
  --auth-mode login `
  --output none

$backendPath = Join-Path $PSScriptRoot "..\terraform\backend.hcl"
@"
resource_group_name  = "$RgName"
storage_account_name = "$StorageName"
container_name       = "$ContainerName"
key                  = "weather.dev.tfstate"
"@ | Set-Content -Path $backendPath -Encoding utf8

Write-Host "Backend ready. Generated terraform/backend.hcl"
Write-Host "Next: cd terraform && terraform init -backend-config=backend.hcl"
