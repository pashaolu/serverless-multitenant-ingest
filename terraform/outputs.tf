output "s3_config_bucket" {
  description = "S3 bucket name for pipeline configs."
  value       = aws_s3_bucket.config.id
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.main.name
}

output "ecs_task_definition_family" {
  description = "ECS task definition family (use with run-task)."
  value       = aws_ecs_task_definition.ingest.family
}

output "aws_region" {
  description = "AWS region."
  value       = var.aws_region
}
