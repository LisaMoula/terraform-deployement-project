#test2
data "azurerm_client_config" "current" {}

resource "random_string" "suffix" {
  length  = 5
  upper   = false
  special = false
}

locals {
  prefix = "${var.project}-${var.environment}"

  tags = merge(var.tags, {
    environment = var.environment
  })

  storage_account_name = "st${var.project}${var.environment}${random_string.suffix.result}"
  key_vault_name       = "kv-${local.prefix}-${random_string.suffix.result}"
  acr_name             = "acr${var.project}${var.environment}${random_string.suffix.result}"
}

resource "azurerm_resource_group" "main" {
  name     = "rg-${local.prefix}"
  location = var.location
  tags     = local.tags
}

module "acr" {
  source = "./modules/acr"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  name                = local.acr_name
  tags                = local.tags
}

module "storage" {
  source = "./modules/storage"

  resource_group_name  = azurerm_resource_group.main.name
  location             = azurerm_resource_group.main.location
  storage_account_name = local.storage_account_name
  containers           = ["landing", "gold"]
  tags                 = local.tags
}

module "keyvault" {
  source = "./modules/keyvault"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  key_vault_name      = local.key_vault_name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  tags                = local.tags

  secrets = {
    "storage-connection-string" = module.storage.primary_connection_string
  }
}

module "app" {
  source = "./modules/app"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  app_name            = "app-${local.prefix}-${random_string.suffix.result}"
  service_plan_name   = "plan-${local.prefix}"
  sku_name            = var.app_service_sku
  docker_image        = var.docker_image
  acr_login_server    = module.acr.login_server
  acr_id              = module.acr.id
  key_vault_id        = module.keyvault.id
  tags                = local.tags

  app_settings = {
    WEBSITES_PORT             = "8501"
    STORAGE_CONNECTION_STRING = "@Microsoft.KeyVault(SecretUri=${module.keyvault.secret_uris["storage-connection-string"]})"
  }
}
