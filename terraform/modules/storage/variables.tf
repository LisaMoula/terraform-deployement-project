variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "storage_account_name" {
  description = "3-24 caractères, minuscules et chiffres, globalement unique."
  type        = string
}

variable "containers" {
  description = "Liste des containers Data Lake (ex : landing, gold)."
  type        = list(string)
  default     = ["landing", "gold"]
}

variable "tags" {
  type    = map(string)
  default = {}
}
