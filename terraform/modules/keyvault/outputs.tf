output "id" {
  value = azurerm_key_vault.this.id
}

output "uri" {
  value = azurerm_key_vault.this.vault_uri
}

output "name" {
  value = azurerm_key_vault.this.name
}

output "secret_uris" {
  description = "Versionless URIs of managed secrets (name => uri)."
  value       = { for k, s in azurerm_key_vault_secret.this : k => s.versionless_id }
}
