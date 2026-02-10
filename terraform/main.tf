locals {
  name_prefix = var.project_name
}

# S3 bucket for pipeline configs (YAML per tenant/source)
resource "aws_s3_bucket" "config" {
  bucket = "${local.name_prefix}-pipeline-configs-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name = "${local.name_prefix}-pipeline-configs"
  }
}

resource "aws_s3_bucket_versioning" "config" {
  bucket = aws_s3_bucket.config.id

  versioning_configuration {
    status = "Enabled"
  }
}

data "aws_caller_identity" "current" {}

# ECS cluster (Fargate)
resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-ingest"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }

  tags = {
    Name = "${local.name_prefix}-ingest"
  }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 0
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# IAM role for ECS task execution (pull image, logs)
resource "aws_iam_role" "ecs_execution" {
  name = "${local.name_prefix}-ecs-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM role for the task itself (S3 read, later Secrets Manager)
resource "aws_iam_role" "ecs_task" {
  name = "${local.name_prefix}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "ecs_task_s3" {
  name = "s3-config-read"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.config.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.config.arn
        Condition = {
          StringEquals = {
            "s3:prefix" = [""]
          }
        }
      }
    ]
  })
}

# Allow ECS task to read secrets (Salesforce, Snowflake credentials)
resource "aws_iam_role_policy" "ecs_task_secrets" {
  name = "secrets-read"
  role = aws_iam_role.ecs_task.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:*"
        Condition = {
          StringEquals = {
            "secretsmanager:VersionStage" = "AWSCURRENT"
          }
        }
      }
    ]
  })
}

# Log group for ingest job
resource "aws_cloudwatch_log_group" "ingest" {
  name              = "/ecs/${local.name_prefix}-ingest"
  retention_in_days = 14

  tags = {
    Name = "${local.name_prefix}-ingest"
  }
}

# ECS task definition (stub: runs ingest job with CONFIG_KEY from override)
resource "aws_ecs_task_definition" "ingest" {
  family                   = "${local.name_prefix}-ingest"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  execution_role_arn = aws_iam_role.ecs_execution.arn
  task_role_arn     = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "ingest"
      image = var.ingest_job_image != "" ? var.ingest_job_image : "public.ecr.aws/docker/library/python:3.12-alpine"
      command = var.ingest_job_image != "" ? null : ["sh", "-c", "echo 'Set TF_VAR_ingest_job_image to your image URI'; exit 0"]

      environment = [
        { name = "S3_CONFIG_BUCKET", value = aws_s3_bucket.config.bucket },
        { name = "AWS_REGION", value = var.aws_region }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ingest.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ingest"
        }
      }
    }
  ])
}
