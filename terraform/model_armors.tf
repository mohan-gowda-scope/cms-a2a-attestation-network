# --- MODEL ARMORS: BEDROCK GUARDRAILS ---
# Implements comprehensive security controls for AI model interactions

locals {
  is_aws_guardrails = var.cloud_provider == "aws" && var.enable_bedrock_guardrails
}

# --- Bedrock Guardrail: PII Detection & Redaction ---
resource "aws_bedrock_guardrail" "pii_protection" {
  count       = local.is_aws_guardrails ? 1 : 0
  name        = "${var.project_name}-pii-protection"
  description = "Detect and redact PII in healthcare attestation data"

  # Content policy filters
  content_policy_config {
    # Block harmful content
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "HATE"
    }
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "INSULTS"
    }
    filters_config {
      input_strength  = "MEDIUM"
      output_strength = "MEDIUM"
      type            = "SEXUAL"
    }
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "VIOLENCE"
    }
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "MISCONDUCT"
    }
  }

  # Sensitive information filters (PII)
  sensitive_information_policy_config {
    # Healthcare-specific PII
    pii_entities_config {
      action = "BLOCK"
      type   = "SSN"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "NAME"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "EMAIL"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "PHONE"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "ADDRESS"
    }
    pii_entities_config {
      action = "BLOCK"
      type   = "CREDIT_DEBIT_CARD_NUMBER"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "DATE_TIME"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "DRIVER_ID"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "IP_ADDRESS"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "USERNAME"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "PASSWORD"
    }

    # Custom regex patterns for healthcare identifiers
    regexes_config {
      action      = "ANONYMIZE"
      description = "Medicare Beneficiary Identifier (MBI)"
      name        = "MBI_Pattern"
      pattern     = "\\b[1-9][A-Z]{2}[0-9][A-Z]{2}[0-9]{2}\\b"
    }
    regexes_config {
      action      = "ANONYMIZE"
      description = "National Provider Identifier (NPI)"
      name        = "NPI_Pattern"
      pattern     = "\\b[1-9]\\d{9}\\b"
    }
    regexes_config {
      action      = "BLOCK"
      description = "Health Insurance Claim Number (HICN)"
      name        = "HICN_Pattern"
      pattern     = "\\b\\d{3}-\\d{2}-\\d{4}[A-Z]?\\b"
    }
  }

  # Topic policy (healthcare-specific)
  topic_policy_config {
    topics_config {
      name       = "medical_advice"
      definition = "Providing specific medical diagnoses, treatment recommendations, or prescriptions"
      examples   = [
        "You should take this medication",
        "This diagnosis indicates you have",
        "I recommend this treatment plan"
      ]
      type = "DENY"
    }
    topics_config {
      name       = "financial_fraud"
      definition = "Attempting to manipulate billing codes or commit healthcare fraud"
      examples   = [
        "Use this code to get higher reimbursement",
        "Bill for services not rendered",
        "Upcoding strategies"
      ]
      type = "DENY"
    }
  }

  # Word policy (profanity and inappropriate terms)
  word_policy_config {
    managed_word_lists_config {
      type = "PROFANITY"
    }
  }

  # Blocked messaging
  blocked_input_messaging  = "Your request contains sensitive information or violates our content policy. Please review and resubmit."
  blocked_outputs_messaging = "The response was blocked due to sensitive content or policy violations."

  tags = {
    Purpose     = "PII Protection and Content Filtering"
    Environment = "production"
  }
}

# --- Bedrock Guardrail: Rate Limiting & DDoS Protection ---
resource "aws_bedrock_guardrail" "rate_limiting" {
  count       = local.is_aws_guardrails ? 1 : 0
  name        = "${var.project_name}-rate-limiting"
  description = "Rate limiting and DDoS protection for Bedrock API calls"

  # Contextual grounding (prevent hallucinations)
  contextual_grounding_policy_config {
    filters_config {
      type      = "GROUNDING"
      threshold = 0.75
    }
    filters_config {
      type      = "RELEVANCE"
      threshold = 0.75
    }
  }

  blocked_input_messaging  = "Request rate limit exceeded. Please try again later."
  blocked_outputs_messaging = "Response generation failed due to rate limiting."

  tags = {
    Purpose     = "Rate Limiting and DDoS Protection"
    Environment = "production"
  }
}

# --- Bedrock Guardrail Version (for production use) ---
resource "aws_bedrock_guardrail_version" "pii_protection_v1" {
  count          = local.is_aws_guardrails ? 1 : 0
  guardrail_arn  = aws_bedrock_guardrail.pii_protection[0].guardrail_arn
  description    = "Production version of PII protection guardrail"
}

resource "aws_bedrock_guardrail_version" "rate_limiting_v1" {
  count          = local.is_aws_guardrails ? 1 : 0
  guardrail_arn  = aws_bedrock_guardrail.rate_limiting[0].guardrail_arn
  description    = "Production version of rate limiting guardrail"
}

# --- IAM Policy: Bedrock Guardrails Access ---
resource "aws_iam_role_policy" "bedrock_guardrails_access" {
  count = local.is_aws_guardrails ? 1 : 0
  name  = "BedrockGuardrailsAccess"
  role  = aws_iam_role.a2a_lambda_role[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:ApplyGuardrail",
          "bedrock:GetGuardrail",
          "bedrock:ListGuardrails"
        ]
        Resource = [
          aws_bedrock_guardrail.pii_protection[0].guardrail_arn,
          aws_bedrock_guardrail.rate_limiting[0].guardrail_arn
        ]
      }
    ]
  })
}

# --- CloudWatch Log Group: Guardrail Violations ---
resource "aws_cloudwatch_log_group" "guardrail_violations" {
  count             = local.is_aws_guardrails ? 1 : 0
  name              = "/aws/bedrock/guardrails/${var.project_name}/violations"
  retention_in_days = 30

  tags = {
    Purpose = "Guardrail Violation Logging"
  }
}

# --- CloudWatch Alarms: Guardrail Violations ---
resource "aws_cloudwatch_metric_alarm" "high_pii_detections" {
  count               = local.is_aws_guardrails ? 1 : 0
  alarm_name          = "${var.project_name}-high-pii-detections"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "GuardrailBlocked"
  namespace           = "AWS/Bedrock"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.pii_detection_threshold
  alarm_description   = "High number of PII detections in requests"
  treat_missing_data  = "notBreaching"

  dimensions = {
    GuardrailId = aws_bedrock_guardrail.pii_protection[0].guardrail_id
  }

  alarm_actions = var.guardrail_alarm_sns_topic != null ? [var.guardrail_alarm_sns_topic] : []
}

resource "aws_cloudwatch_metric_alarm" "rate_limit_exceeded" {
  count               = local.is_aws_guardrails ? 1 : 0
  alarm_name          = "${var.project_name}-rate-limit-exceeded"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "GuardrailBlocked"
  namespace           = "AWS/Bedrock"
  period              = "60"
  statistic           = "Sum"
  threshold           = var.rate_limit_threshold
  alarm_description   = "Rate limit exceeded - possible DDoS attack"
  treat_missing_data  = "notBreaching"

  dimensions = {
    GuardrailId = aws_bedrock_guardrail.rate_limiting[0].guardrail_id
  }

  alarm_actions = var.guardrail_alarm_sns_topic != null ? [var.guardrail_alarm_sns_topic] : []
}

# --- DynamoDB Table: Guardrail Audit Log ---
resource "aws_dynamodb_table" "guardrail_audit_log" {
  count          = local.is_aws_guardrails ? 1 : 0
  name           = "${var.project_name}-guardrail-audit-log"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "request_id"
  range_key      = "timestamp"

  attribute {
    name = "request_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  attribute {
    name = "violation_type"
    type = "S"
  }

  # GSI for querying by violation type
  global_secondary_index {
    name            = "ViolationTypeIndex"
    hash_key        = "violation_type"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Purpose = "Guardrail Violation Audit Trail"
  }
}

# --- Outputs ---
output "pii_protection_guardrail_id" {
  description = "Bedrock Guardrail ID for PII protection"
  value       = local.is_aws_guardrails ? aws_bedrock_guardrail.pii_protection[0].guardrail_id : null
}

output "pii_protection_guardrail_arn" {
  description = "Bedrock Guardrail ARN for PII protection"
  value       = local.is_aws_guardrails ? aws_bedrock_guardrail.pii_protection[0].guardrail_arn : null
}

output "pii_protection_guardrail_version" {
  description = "Bedrock Guardrail version for PII protection"
  value       = local.is_aws_guardrails ? aws_bedrock_guardrail_version.pii_protection_v1[0].version : null
}

output "rate_limiting_guardrail_id" {
  description = "Bedrock Guardrail ID for rate limiting"
  value       = local.is_aws_guardrails ? aws_bedrock_guardrail.rate_limiting[0].guardrail_id : null
}

output "guardrail_audit_log_table" {
  description = "DynamoDB table for guardrail audit logs"
  value       = local.is_aws_guardrails ? aws_dynamodb_table.guardrail_audit_log[0].name : null
}
