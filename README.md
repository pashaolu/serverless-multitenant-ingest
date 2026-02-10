# serverless-mt-ingest

Multi-tenant, configuration-driven CRM data ingestion on AWS. Ingests from Salesforce and HubSpot into Snowflake (raw data as VARIANT), orchestrated by ECS Fargate and EventBridge Scheduler.

## Prerequisites

- AWS account
- Terraform >= 1.x
- Docker (for building the ingest job image)
- Python 3.12+ with `uv` (for local development)

## Project structure

- `terraform/` – AWS infrastructure (S3, ECS, EventBridge)
- `ingest_job/` – Python job that reads config from S3 and runs dlt pipelines
- `docs/` – Architecture and runbooks

## Quick start

1. Copy `.env.example` to `.env` and set variables.
2. Build and push the ingest job image to ECR (see `ingest_job/README.md`).
3. From `terraform/`: `terraform init && terraform plan && terraform apply`.

## Staged development

The project is built in stages; each stage is a separate commit:

1. **Stage 1** – Repo skeleton, Terraform (S3, ECS Fargate, IAM), stub ingest job that reads config from S3 and logs it.
2. Stage 2 – dlt + Salesforce → Snowflake (VARIANT), secrets.
3. Stage 3 – Multi-tenant config layout, EventBridge Scheduler per config.
4. Stage 4 – HubSpot support.
5. Stage 5 – Docs and polish.

Details and deployment steps will be expanded in later stages.
