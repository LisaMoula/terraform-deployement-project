variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "app_name" {
  type = string
}

variable "service_plan_name" {
  type = string
}

variable "sku_name" {
  description = "SKU du plan App Service (ex : B1)."
  type        = string
  default     = "B1"
}

variable "docker_image" {
  description = "Image name and tag (e.g. weather-dashboard:latest)."
  type        = string
}

variable "acr_login_server" {
  type = string
}

variable "acr_id" {
  type = string
}

variable "key_vault_id" {
  type = string
}

variable "app_settings" {
  description = "Variables d'environnement de l'app (dont WEBSITES_PORT)."
  type        = map(string)
  default     = {}
  sensitive   = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
