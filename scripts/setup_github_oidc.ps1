<#
Sets up GitHub Actions OIDC auth to Azure for the CI pipeline.

Creates an Azure AD app + service principal with federated credentials (no
client secret), grants it the roles needed to run terraform plan, and pushes
the required secrets to the GitHub repo.

Prereqs: az login (Owner/rights to create AD apps + role assignments), gh auth login.

  ./scripts/setup_github_oidc.ps1
#>

$ErrorActionPreference = "Stop"

$Repo        = "LisaMoula/terraform-deployement-project"
$AppName     = "gh-oidc-weather-ci"
$KeyVaultName = "kv-weather-dev-4e95s"

# tfstate backend (matches terraform/backend.hcl)
$TfstateRg        = "rg-tfstate-weather"
$TfstateSa        = "sttfstateweather4574"
$TfstateContainer = "tfstate"

$SubId    = az account show --query id -o tsv
$TenantId = az account show --query tenantId -o tsv

Write-Host "==> Creating AAD app $AppName"
$AppId = az ad app create --display-name $AppName --query appId -o tsv
az ad sp create --id $AppId --output none 2>$null

# Federated credentials: main branch, pull requests.
$subjects = @{
  "gh-main" = "repo:${Repo}:ref:refs/heads/main"
  "gh-pr"   = "repo:${Repo}:pull_request"
}
foreach ($name in $subjects.Keys) {
  $body = @{
    name      = $name
    issuer    = "https://token.actions.githubusercontent.com"
    subject   = $subjects[$name]
    audiences = @("api://AzureADTokenExchange")
  } | ConvertTo-Json -Compress
  $body | az ad app federated-credential create --id $AppId --parameters "@-" --output none
}

# Scoped roles (no subscription-wide Contributor).
$appRg     = "rg-weather-dev"
$tfstateId = az storage account show --name $TfstateSa --resource-group $TfstateRg --query id -o tsv

Write-Host "==> Contributor on $appRg (plan refreshes app resources)"
az role assignment create --assignee $AppId --role "Contributor" `
  --scope "/subscriptions/$SubId/resourceGroups/$appRg" --output none

Write-Host "==> Storage Blob Data Contributor on tfstate account (remote state)"
az role assignment create --assignee $AppId --role "Storage Blob Data Contributor" `
  --scope $tfstateId --output none

Write-Host "==> Granting Key Vault secret read (plan reads a KV secret)"
az keyvault set-policy --name $KeyVaultName --spn $AppId `
  --secret-permissions get list --output none

Write-Host "==> Pushing GitHub secrets"
gh secret set AZURE_CLIENT_ID       --repo $Repo --body $AppId
gh secret set AZURE_TENANT_ID       --repo $Repo --body $TenantId
gh secret set AZURE_SUBSCRIPTION_ID --repo $Repo --body $SubId
gh secret set TFSTATE_RG            --repo $Repo --body $TfstateRg
gh secret set TFSTATE_SA            --repo $Repo --body $TfstateSa
gh secret set TFSTATE_CONTAINER     --repo $Repo --body $TfstateContainer

Write-Host "Done. CI can now authenticate to Azure via OIDC."
