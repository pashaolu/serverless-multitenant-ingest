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
  description = "Full ECR image URI for the ingest job (e.g. 123456789.dkr.ecr.us-east-1.amazonaws.com/mt-ingest:latest)."
  type        = string
  default     = ""
}
