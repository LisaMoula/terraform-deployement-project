<#
Sets up the CD environments and their OIDC federated credentials.

- Adds federated credentials for the GitHub "dev" and "prod" environments.
- Creates the GitHub environments: dev (no protection), prod (required reviewer).

Prereqs: az login, gh auth login. Run after setup_github_oidc.ps1.

  ./scripts/setup_cd.ps1
#>

$ErrorActionPreference = "Stop"

$Repo    = "LisaMoula/terraform-deployement-project"
$AppName = "gh-oidc-weather-ci"
$UserId  = 120172831   # LisaMoula (also used as required reviewer)
# OIDC subject prefix uses immutable numeric ids on this account.
$Prefix  = "repo:LisaMoula@120172831/terraform-deployement-project@1314677143"

$AppId = az ad app list --display-name $AppName --query "[0].appId" -o tsv

foreach ($envName in @("dev", "prod")) {
  Write-Host "==> Federated credential for environment:$envName"
  $body = @{
    name      = "gh-env-$envName"
    issuer    = "https://token.actions.githubusercontent.com"
    subject   = "${Prefix}:environment:$envName"
    audiences = @("api://AzureADTokenExchange")
  } | ConvertTo-Json -Compress
  $body | az ad app federated-credential create --id $AppId --parameters "@-" --output none
}

Write-Host "==> GitHub environment: dev (no protection)"
gh api --method PUT "repos/$Repo/environments/dev" --silent

Write-Host "==> GitHub environment: prod (required reviewer)"
$prodBody = @{
  reviewers = @(@{ type = "User"; id = $UserId })
} | ConvertTo-Json -Compress
$prodBody | gh api --method PUT "repos/$Repo/environments/prod" --input - --silent

Write-Host "Done. CD environments ready (prod requires manual approval)."
