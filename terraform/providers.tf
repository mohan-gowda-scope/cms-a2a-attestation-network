terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "default" # As per user rules: Use AWS Profile

  default_tags {
    tags = {
      Project   = "CMS-A2A-Attestation"
      ManagedBy = "Terraform"
    }
  }
}
