resource "azurerm_container_registry" "this" {
  name                = var.name
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "Basic"
  # no static admin login/password: the App Service pulls images via its
  # managed identity + the AcrPull role instead (see modules/app/main.tf)
  admin_enabled       = false
  tags                = var.tags
}
