variable "name" {
  description = "5-50 alphanumeric chars, globally unique."
  type        = string
}

variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}
