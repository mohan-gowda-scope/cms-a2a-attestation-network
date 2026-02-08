# CMS A2A Network - Consolidated Multi-Cloud Infrastructure
# Target provider is controlled via the 'cloud_provider' variable

# --- AWS PROVIDER LOGIC ---

locals {
  is_aws_core = var.cloud_provider == "aws"
}

# Add conditional logic to existing main.tf resources
# (Note: Agent specific resources moved to aws_agents.tf)

# API Gateway: Central A2A Orchestration Endpoint
resource "aws_api_gateway_rest_api" "a2a_api_core" {
  count       = local.is_aws_core ? 1 : 0
  name        = "${var.project_name}-gateway"
  description = "A2A Trust Network API Gateway"
}

resource "aws_api_gateway_deployment" "a2a_deployment_core" {
  count       = local.is_aws_core ? 1 : 0
  rest_api_id = aws_api_gateway_rest_api.a2a_api_core[0].id
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "a2a_stage_core" {
  count         = local.is_aws_core ? 1 : 0
  deployment_id = aws_api_gateway_deployment.a2a_deployment_core[0].id
  rest_api_id   = aws_api_gateway_rest_api.a2a_api_core[0].id
  stage_name    = "prod"
}

# S3 & Trigger System (Conditional)
resource "aws_s3_bucket" "claims_dropbox_core" {
  count         = local.is_aws_core ? 1 : 0
  bucket        = "${var.project_name}-claims-dropbox-demo"
  force_destroy = true
}

# --- OUTPUTS ---

output "stack_info" {
  value = {
    provider = var.cloud_provider
    region   = var.aws_region
    status   = "Validated"
  }
}

output "aws_api_endpoint" {
  value = local.is_aws_core ? "${aws_api_gateway_stage.a2a_stage_core[0].invoke_url}/prod" : "N/A"
}
