variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "cms-a2a-attestation"
}

variable "cloud_provider" {
  description = "Target cloud provider: 'aws' or 'gcp'"
  type        = string
  default     = "aws"
}
