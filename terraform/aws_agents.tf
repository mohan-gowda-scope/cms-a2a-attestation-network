# --- AWS AGENT MESH (10 AGENTS) ---

locals {
  is_aws = var.cloud_provider == "aws"
}

# --- Shared Infrastructure ---
resource "aws_iam_role" "a2a_lambda_role" {
  count = local.is_aws ? 1 : 0
  name  = "${var.project_name}-lambda-full-stack-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

# --- 10 Agent Definitions ---
locals {
  agent_list = [
    "provider", "clearinghouse", "cms", "payer", "pbm", 
    "lab", "auditor", "credentialing", "patient", "research"
  ]
}

data "archive_file" "agent_zips" {
  for_each    = local.is_aws ? toset(local.agent_list) : []
  type        = "zip"
  source_file = "${path.module}/../aws_lambda/${each.key}_agent.py"
  output_path = "${path.module}/${each.key}_agent.zip"
}

resource "aws_lambda_function" "mesh_agents" {
  for_each         = local.is_aws ? toset(local.agent_list) : []
  filename         = data.archive_file.agent_zips[each.key].output_path
  function_name    = "${var.project_name}-${each.key}-aws"
  role             = aws_iam_role.a2a_lambda_role[0].arn
  handler          = "${each.key}_agent.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.agent_zips[each.key].output_base64sha256

  environment {
    variables = {
      CLOUD_PROVIDER = "aws"
      LEDGER_TABLE   = local.is_aws ? aws_dynamodb_table.a2a_ledger[0].name : ""
    }
  }
}

# --- AWS Multi-Agent Orchestration Ledger ---
resource "aws_dynamodb_table" "a2a_ledger" {
  count          = local.is_aws ? 1 : 0
  name           = "${var.project_name}-universal-ledger"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "pk"
  range_key      = "sk"

  attribute {
    name = "pk"
    type = "S"
  }
  attribute {
    name = "sk"
    type = "S"
  }

  server_side_encryption { enabled = true }
}

# Permissions for AI (Bedrock)
resource "aws_iam_role_policy" "bedrock_access" {
  count = local.is_aws ? 1 : 0
  name  = "BedrockAIParity"
  role  = aws_iam_role.a2a_lambda_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = ["bedrock:InvokeModel"]
        Effect = "Allow"
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-5-sonnet-*"
      },
      {
        Action = ["dynamodb:*"]
        Effect = "Allow"
        Resource = "*"
      },
      {
        Action = ["logs:*"]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}
