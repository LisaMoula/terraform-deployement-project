output "resource_group_name" {
  description = "Nom du Resource Group applicatif."
  value       = azurerm_resource_group.main.name
}

output "location" {
  description = "Région Azure ciblée."
  value       = var.location
}

output "storage_account_name" {
  description = "Nom du Storage Account (Data Lake)."
  value       = module.storage.name
}

output "data_lake_containers" {
  description = "Containers Data Lake créés (Landing / Gold)."
  value       = module.storage.container_names
}

output "key_vault_uri" {
  description = "URI du Key Vault."
  value       = module.keyvault.uri
}

output "acr_login_server" {
  description = "ACR login server (push target)."
  value       = module.acr.login_server
}

output "app_url" {
  description = "URL publique de l'application Streamlit."
  value       = "https://${module.app.default_hostname}"
}
