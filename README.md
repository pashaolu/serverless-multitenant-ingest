# serverless-mt-ingest

Multi-tenant, configuration-driven CRM data ingestion on AWS. Ingests from Salesforce and HubSpot into Snowflake (raw data as VARIANT), orchestrated by ECS Fargate and EventBridge Scheduler.

## dlt (data load tool)

This project uses **[dlt](https://dlthub.com)** (data load tool) to run the actual pipelines:

- **Sources**: Salesforce (Stage 2), HubSpot (Stage 4) via dlt verified sources.
- **Destination**: Snowflake; credentials and dataset/schema are config-driven, credentials stored in AWS Secrets Manager.

Pipeline config is YAML in S3; the ingest job reads config, resolves credentials from Secrets Manager, and runs the appropriate dlt source into Snowflake. Data is loaded with dlt’s normal typing; for VARIANT-style raw storage you can use Snowflake’s JSONL loader or add views as needed.

- [dlt docs](https://dlthub.com/docs)
- [Salesforce source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/salesforce)
- [Snowflake destination](https://dlthub.com/docs/dlt-ecosystem/destinations/snowflake)

## Prerequisites

- AWS account
- Terraform >= 1.x
- Docker (for building the ingest job image)
- Python 3.12+ with `uv` (for local development)
- Snowflake account (for destination)

## Project structure

- `terraform/` – AWS infrastructure (S3, ECS, EventBridge, IAM for Secrets Manager)
- `ingest_job/` – Python job that reads config from S3 and runs dlt pipelines (Salesforce → Snowflake)
- `docs/` – Architecture and runbooks

## Quick start

1. Copy `.env.example` to `.env` and set variables.
2. Build and push the ingest job image to ECR (see `ingest_job/README.md`).
3. From `terraform/`: `terraform init && terraform plan && terraform apply`.

## Staged development

The project is built in stages; each stage is a separate commit:

1. **Stage 1** – Repo skeleton, Terraform (S3, ECS Fargate, IAM), stub ingest job that reads config from S3 and logs it.
2. **Stage 2** – dlt + Salesforce → Snowflake, config-driven pipeline, credentials from AWS Secrets Manager.
3. Stage 3 – Multi-tenant config layout, EventBridge Scheduler per config.
4. Stage 4 – HubSpot support.
5. Stage 5 – Docs and polish.

Details and deployment steps will be expanded in later stages.
