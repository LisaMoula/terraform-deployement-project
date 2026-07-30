resource "azurerm_service_plan" "this" {
  name                = var.service_plan_name
  resource_group_name = var.resource_group_name
  location            = var.location
  os_type             = "Linux"
  sku_name            = var.sku_name
  tags                = var.tags
}

resource "azurerm_linux_web_app" "this" {
  name                = var.app_name
  resource_group_name = var.resource_group_name
  location            = var.location
  service_plan_id     = azurerm_service_plan.this.id
  https_only          = true
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }

  site_config {
    always_on                               = true
    container_registry_use_managed_identity = true

    application_stack {
      docker_image_name   = var.docker_image
      docker_registry_url = "https://${var.acr_login_server}"
    }
  }

  app_settings = var.app_settings
}

# grants image pull rights on the ACR to the app's managed identity, replacing
# the registry's disabled admin login/password entirely
resource "azurerm_role_assignment" "acr_pull" {
  scope                = var.acr_id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_linux_web_app.this.identity[0].principal_id
}

resource "azurerm_key_vault_access_policy" "app" {
  key_vault_id = var.key_vault_id
  tenant_id    = azurerm_linux_web_app.this.identity[0].tenant_id
  object_id    = azurerm_linux_web_app.this.identity[0].principal_id

  secret_permissions = ["Get", "List"]
}
