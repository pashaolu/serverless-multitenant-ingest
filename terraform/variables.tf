variable "aws_region" {
  description = "AWS region for resources."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name used for resource naming."
  type        = string
}

variable "ingest_job_image" {
  description = "Full ECR image URI for the ingest job (e.g. 123456789.dkr.ecr.us-east-1.amazonaws.com/serverless-multitenant-ingest:latest)."
  type        = string
  default     = ""
}

variable "ecs_subnet_ids" {
  description = "Subnet IDs for the ECS Fargate task (e.g. private subnets with NAT or public subnets)."
  type        = list(string)
}

variable "ecs_security_group_ids" {
  description = "Security group IDs for the ECS Fargate task (must allow outbound to S3, Secrets Manager, and the internet for CRM/Snowflake)."
  type        = list(string)
}

variable "scheduler_timezone" {
  description = "Timezone for cron schedules in pipeline configs (e.g. Europe/London)."
  type        = string
  default     = "UTC"
}
