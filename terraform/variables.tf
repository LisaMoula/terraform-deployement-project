variable "project" {
  description = "Nom court du projet, utilisé pour nommer les ressources."
  type        = string
  default     = "weather"
}

variable "environment" {
  description = "Environnement cible (dev, prod)."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment doit être 'dev' ou 'prod'."
  }
}

variable "location" {
  description = "Région Azure."
  type        = string
  default     = "France Central"
}

variable "app_service_sku" {
  description = "SKU du plan App Service (B1 = Basic, éco pour la dev)."
  type        = string
  default     = "B1"
}

variable "docker_image" {
  description = "Image name and tag pushed to ACR."
  type        = string
  default     = "weather-dashboard:latest"
}

variable "tags" {
  description = "Tags communs appliqués à toutes les ressources."
  type        = map(string)
  default = {
    project    = "weather-dashboard-test"
    managed_by = "terraform"
    course     = "ESGI-DevOps"
  }
}
