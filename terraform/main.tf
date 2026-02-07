# DynamoDB Table for Payer Authorizations (Phase 3)
resource "aws_dynamodb_table" "payer_auth_ledger" {
  name           = "${var.project_name}-payer-auths"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "auth_id"

  attribute {
    name = "auth_id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  tags = {
    Name = "PayerAuthLedger"
  }
}

# S3 Bucket for Claim/Attestation Triggers (Phase 3)
resource "aws_s3_bucket" "claims_dropbox" {
  bucket = "${var.project_name}-claims-dropbox-${uuid()}"
  force_destroy = true
}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.claims_dropbox.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.provider_agent.arn
    events              = ["s3:ObjectCreated:*"]
  }

  depends_on = [aws_lambda_permission.allow_s3_trigger]
}

resource "aws_lambda_permission" "allow_s3_trigger" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.provider_agent.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.claims_dropbox.arn
}

# Zip the Lambda code (Payer Agent)
data "archive_file" "payer_zip" {
  type        = "zip"
  source_file = "${path.module}/../lambda/payer_agent.py"
  output_path = "${path.module}/payer_agent.zip"
}

# Lambda Function (Payer Agent)
resource "aws_lambda_function" "payer_agent" {
  filename         = data.archive_file.payer_zip.output_path
  function_name    = "${var.project_name}-payer"
  role             = aws_iam_role.lambda_role.arn
  handler          = "payer_agent.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.payer_zip.output_base64sha256

  environment {
    variables = {
      AUTH_TABLE = aws_dynamodb_table.payer_auth_ledger.name
    }
  }
}

# Lambda Permission for API Gateway (Payer)
resource "aws_lambda_permission" "apigw_payer" {
  statement_id  = "AllowPayerExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.payer_agent.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.a2a_api.execution_arn}/*/*"
}

# Add Payer API Resource
resource "aws_api_gateway_resource" "payer_resource" {
  rest_api_id = aws_api_gateway_rest_api.a2a_api.id
  parent_id   = aws_api_gateway_rest_api.a2a_api.root_resource_id
  path_part   = "payer"
}

resource "aws_api_gateway_method" "payer_post" {
  rest_api_id   = aws_api_gateway_rest_api.a2a_api.id
  resource_id   = aws_api_gateway_resource.payer_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "payer_integration" {
  rest_api_id             = aws_api_gateway_rest_api.a2a_api.id
  resource_id             = aws_api_gateway_resource.payer_resource.id
  http_method             = aws_api_gateway_method.payer_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.payer_agent.invoke_arn
}

# Update Clearinghouse ENV
resource "aws_lambda_function" "clearinghouse" {
  filename         = data.archive_file.clearinghouse_zip.output_path
  function_name    = "${var.project_name}-clearinghouse"
  role             = aws_iam_role.lambda_role.arn
  handler          = "clearinghouse_agent.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.clearinghouse_zip.output_base64sha256

  environment {
    variables = {
      LEDGER_TABLE   = aws_dynamodb_table.attestation_ledger.name
      CMS_A2A_ENDPOINT = "${aws_api_gateway_stage.a2a_stage.invoke_url}/cms"
      PAYER_A2A_ENDPOINT = "${aws_api_gateway_stage.a2a_stage.invoke_url}/payer"
    }
  }
}

# Update IAM for new tables
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Effect   = "Allow"
        Resource = [
            aws_dynamodb_table.attestation_ledger.arn,
            aws_dynamodb_table.payer_auth_ledger.arn
        ]
      },
      {
        Action = [
          "bedrock:InvokeModel"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Outputs
output "api_endpoint" {
  value = "${aws_api_gateway_stage.a2a_stage.invoke_url}/cms"
}

output "clearinghouse_endpoint" {
  value = "${aws_api_gateway_stage.a2a_stage.invoke_url}/clearinghouse"
}

output "claims_bucket" {
  value = aws_s3_bucket.claims_dropbox.id
}
