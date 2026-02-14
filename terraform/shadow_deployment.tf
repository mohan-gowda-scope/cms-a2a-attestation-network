# --- SHADOW DEPLOYMENT INFRASTRUCTURE ---
# Implements Lambda alias-based shadow deployment with traffic shifting

locals {
  is_aws_shadow = var.cloud_provider == "aws" && var.enable_shadow_deployment
}

# --- Lambda Versions (Published on every deployment) ---
resource "aws_lambda_function" "mesh_agents_versioned" {
  for_each         = local.is_aws_shadow ? toset(local.agent_list) : []
  filename         = data.archive_file.agent_zips[each.key].output_path
  function_name    = "${var.project_name}-${each.key}-aws"
  role             = aws_iam_role.a2a_lambda_role[0].arn
  handler          = "${each.key}_agent.lambda_handler"
  runtime          = "python3.11"
  source_code_hash = data.archive_file.agent_zips[each.key].output_base64sha256
  publish          = true  # CRITICAL: Publish new version on every deployment

  environment {
    variables = {
      CLOUD_PROVIDER = "aws"
      LEDGER_TABLE   = local.is_aws ? aws_dynamodb_table.a2a_ledger[0].name : ""
      DEPLOYMENT_ENV = "production"
    }
  }

  # Enable X-Ray tracing for shadow deployment monitoring
  tracing_config {
    mode = "Active"
  }

  # Enable VPC configuration if needed
  dynamic "vpc_config" {
    for_each = var.lambda_vpc_config != null ? [var.lambda_vpc_config] : []
    content {
      subnet_ids         = vpc_config.value.subnet_ids
      security_group_ids = vpc_config.value.security_group_ids
    }
  }

  tags = {
    Environment = "production"
    ManagedBy   = "terraform"
    ShadowDeployment = "enabled"
  }
}

# --- Lambda Alias: PRODUCTION (Stable) ---
resource "aws_lambda_alias" "production" {
  for_each         = local.is_aws_shadow ? toset(local.agent_list) : []
  name             = "production"
  description      = "Production alias for stable traffic"
  function_name    = aws_lambda_function.mesh_agents_versioned[each.key].function_name
  function_version = aws_lambda_function.mesh_agents_versioned[each.key].version

  # Routing configuration for traffic shifting
  routing_config {
    additional_version_weights = {
      # Shadow version gets traffic_split_percentage (default 10%)
      # This will be updated by deployment scripts
    }
  }

  lifecycle {
    ignore_changes = [
      function_version,
      routing_config
    ]
  }
}

# --- Lambda Alias: SHADOW (Canary/Testing) ---
resource "aws_lambda_alias" "shadow" {
  for_each         = local.is_aws_shadow ? toset(local.agent_list) : []
  name             = "shadow"
  description      = "Shadow alias for canary deployments"
  function_name    = aws_lambda_function.mesh_agents_versioned[each.key].function_name
  function_version = aws_lambda_function.mesh_agents_versioned[each.key].version

  lifecycle {
    ignore_changes = [function_version]
  }
}

# --- DynamoDB Table: Deployment State Management ---
resource "aws_dynamodb_table" "deployment_state" {
  count          = local.is_aws_shadow ? 1 : 0
  name           = "${var.project_name}-deployment-state"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "agent_name"
  range_key      = "deployment_id"

  attribute {
    name = "agent_name"
    type = "S"
  }

  attribute {
    name = "deployment_id"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  # GSI for querying by status
  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "status"
    range_key       = "deployment_id"
    projection_type = "ALL"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    Purpose = "Shadow Deployment State Management"
  }
}

# --- CloudWatch Log Groups for Shadow Deployment Monitoring ---
resource "aws_cloudwatch_log_group" "shadow_deployment_logs" {
  for_each          = local.is_aws_shadow ? toset(local.agent_list) : []
  name              = "/aws/lambda/${var.project_name}-${each.key}-aws/shadow-deployment"
  retention_in_days = 7

  tags = {
    Purpose = "Shadow Deployment Monitoring"
  }
}

# --- CloudWatch Alarms: Shadow vs Production Comparison ---
resource "aws_cloudwatch_metric_alarm" "shadow_error_rate" {
  for_each            = local.is_aws_shadow ? toset(local.agent_list) : []
  alarm_name          = "${var.project_name}-${each.key}-shadow-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.shadow_error_threshold
  alarm_description   = "Shadow deployment error rate exceeded threshold"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.mesh_agents_versioned[each.key].function_name
    Resource     = "${aws_lambda_function.mesh_agents_versioned[each.key].function_name}:shadow"
  }

  alarm_actions = var.shadow_alarm_sns_topic != null ? [var.shadow_alarm_sns_topic] : []
}

resource "aws_cloudwatch_metric_alarm" "shadow_duration_anomaly" {
  for_each            = local.is_aws_shadow ? toset(local.agent_list) : []
  alarm_name          = "${var.project_name}-${each.key}-shadow-duration-anomaly"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Average"
  threshold           = var.shadow_duration_threshold_ms
  alarm_description   = "Shadow deployment duration anomaly detected"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.mesh_agents_versioned[each.key].function_name
    Resource     = "${aws_lambda_function.mesh_agents_versioned[each.key].function_name}:shadow"
  }

  alarm_actions = var.shadow_alarm_sns_topic != null ? [var.shadow_alarm_sns_topic] : []
}

# --- SNS Topic for Shadow Deployment Alerts (Optional) ---
resource "aws_sns_topic" "shadow_deployment_alerts" {
  count = local.is_aws_shadow && var.create_shadow_sns_topic ? 1 : 0
  name  = "${var.project_name}-shadow-deployment-alerts"

  tags = {
    Purpose = "Shadow Deployment Notifications"
  }
}

# --- IAM Role for CodeDeploy (Traffic Shifting) ---
resource "aws_iam_role" "codedeploy_lambda" {
  count = local.is_aws_shadow ? 1 : 0
  name  = "${var.project_name}-codedeploy-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "codedeploy.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "codedeploy_lambda" {
  count      = local.is_aws_shadow ? 1 : 0
  role       = aws_iam_role.codedeploy_lambda[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSCodeDeployRoleForLambda"
}

# --- CodeDeploy Application ---
resource "aws_codedeploy_app" "lambda_deployment" {
  count            = local.is_aws_shadow ? 1 : 0
  name             = "${var.project_name}-lambda-deployment"
  compute_platform = "Lambda"
}

# --- CodeDeploy Deployment Groups (One per agent) ---
resource "aws_codedeploy_deployment_group" "lambda_agents" {
  for_each               = local.is_aws_shadow ? toset(local.agent_list) : []
  app_name               = aws_codedeploy_app.lambda_deployment[0].name
  deployment_group_name  = "${each.key}-agent-deployment-group"
  service_role_arn       = aws_iam_role.codedeploy_lambda[0].arn
  deployment_config_name = var.codedeploy_config_name

  auto_rollback_configuration {
    enabled = true
    events  = ["DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM"]
  }

  alarm_configuration {
    enabled = true
    alarms  = [
      aws_cloudwatch_metric_alarm.shadow_error_rate[each.key].alarm_name,
      aws_cloudwatch_metric_alarm.shadow_duration_anomaly[each.key].alarm_name
    ]
  }

  deployment_style {
    deployment_option = "WITH_TRAFFIC_CONTROL"
    deployment_type   = "BLUE_GREEN"
  }
}

# --- Outputs ---
output "lambda_production_aliases" {
  description = "Production Lambda alias ARNs"
  value = {
    for k, v in aws_lambda_alias.production : k => v.arn
  }
}

output "lambda_shadow_aliases" {
  description = "Shadow Lambda alias ARNs"
  value = {
    for k, v in aws_lambda_alias.shadow : k => v.arn
  }
}

output "deployment_state_table" {
  description = "DynamoDB table for deployment state management"
  value       = local.is_aws_shadow ? aws_dynamodb_table.deployment_state[0].name : null
}

output "codedeploy_app_name" {
  description = "CodeDeploy application name"
  value       = local.is_aws_shadow ? aws_codedeploy_app.lambda_deployment[0].name : null
}
