# --- MODEL ARMOR VARIABLES ---

variable "enable_bedrock_guardrails" {
  description = "Enable Bedrock Guardrails for model armors"
  type        = bool
  default     = true
}

variable "pii_detection_threshold" {
  description = "Threshold for PII detection alarms (number of detections per 5 minutes)"
  type        = number
  default     = 50
}

variable "rate_limit_threshold" {
  description = "Threshold for rate limiting alarms (requests per minute)"
  type        = number
  default     = 100
}

variable "guardrail_alarm_sns_topic" {
  description = "SNS topic ARN for guardrail alarms (optional)"
  type        = string
  default     = null
}

variable "guardrail_audit_retention_days" {
  description = "Number of days to retain guardrail audit logs in DynamoDB (TTL)"
  type        = number
  default     = 90
}

variable "content_filter_strength" {
  description = "Strength of content filtering (LOW, MEDIUM, HIGH)"
  type        = string
  default     = "HIGH"
  validation {
    condition     = contains(["LOW", "MEDIUM", "HIGH"], var.content_filter_strength)
    error_message = "Content filter strength must be LOW, MEDIUM, or HIGH."
  }
}

variable "enable_contextual_grounding" {
  description = "Enable contextual grounding to prevent hallucinations"
  type        = bool
  default     = true
}

variable "grounding_threshold" {
  description = "Threshold for contextual grounding (0.0-1.0)"
  type        = number
  default     = 0.75
  validation {
    condition     = var.grounding_threshold >= 0.0 && var.grounding_threshold <= 1.0
    error_message = "Grounding threshold must be between 0.0 and 1.0."
  }
}
