# --- SHADOW DEPLOYMENT VARIABLES ---

variable "enable_shadow_deployment" {
  description = "Enable shadow deployment infrastructure"
  type        = bool
  default     = true
}

variable "traffic_split_percentage" {
  description = "Percentage of traffic to route to shadow deployment (0-50)"
  type        = number
  default     = 10
  validation {
    condition     = var.traffic_split_percentage >= 0 && var.traffic_split_percentage <= 50
    error_message = "Traffic split percentage must be between 0 and 50."
  }
}

variable "shadow_error_threshold" {
  description = "Error count threshold for shadow deployment alarms"
  type        = number
  default     = 5
}

variable "shadow_duration_threshold_ms" {
  description = "Duration threshold in milliseconds for shadow deployment alarms"
  type        = number
  default     = 10000
}

variable "shadow_alarm_sns_topic" {
  description = "SNS topic ARN for shadow deployment alarms (optional)"
  type        = string
  default     = null
}

variable "create_shadow_sns_topic" {
  description = "Create SNS topic for shadow deployment alerts"
  type        = bool
  default     = false
}

variable "codedeploy_config_name" {
  description = "CodeDeploy deployment configuration name"
  type        = string
  default     = "CodeDeployDefault.LambdaLinear10PercentEvery3Minutes"
  validation {
    condition = contains([
      "CodeDeployDefault.LambdaCanary10Percent5Minutes",
      "CodeDeployDefault.LambdaCanary10Percent10Minutes",
      "CodeDeployDefault.LambdaCanary10Percent15Minutes",
      "CodeDeployDefault.LambdaCanary10Percent30Minutes",
      "CodeDeployDefault.LambdaLinear10PercentEvery1Minute",
      "CodeDeployDefault.LambdaLinear10PercentEvery2Minutes",
      "CodeDeployDefault.LambdaLinear10PercentEvery3Minutes",
      "CodeDeployDefault.LambdaLinear10PercentEvery10Minutes",
      "CodeDeployDefault.LambdaAllAtOnce"
    ], var.codedeploy_config_name)
    error_message = "Invalid CodeDeploy configuration name."
  }
}

variable "lambda_vpc_config" {
  description = "VPC configuration for Lambda functions (optional)"
  type = object({
    subnet_ids         = list(string)
    security_group_ids = list(string)
  })
  default = null
}

variable "deployment_retention_days" {
  description = "Number of days to retain deployment state records"
  type        = number
  default     = 30
}
