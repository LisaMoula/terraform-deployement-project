output "default_hostname" {
  value = azurerm_linux_web_app.this.default_hostname
}

output "principal_id" {
  description = "Object ID de l'identité managée de l'app."
  value       = azurerm_linux_web_app.this.identity[0].principal_id
}
