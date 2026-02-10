# serverless-mt-ingest

Multi-tenant, configuration-driven CRM data ingestion on AWS. Ingests from Salesforce and HubSpot into Snowflake (raw data as VARIANT), orchestrated by ECS Fargate and EventBridge Scheduler.

## dlt (data load tool)

This project uses **[dlt](https://dlthub.com)** (data load tool) to run the actual pipelines:

- **Sources**: Salesforce, HubSpot via dlt verified sources.
- **Destination**: Snowflake; credentials and dataset/schema are config-driven, credentials stored in AWS Secrets Manager.

Pipeline config is YAML in S3; the ingest job reads config, resolves credentials from Secrets Manager, and runs the appropriate dlt source into Snowflake. Data is loaded with dlt’s normal typing; for VARIANT-style raw storage you can use Snowflake’s JSONL loader or add views as needed.

- [dlt docs](https://dlthub.com/docs)
- [Salesforce source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/salesforce)
- [HubSpot source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/hubspot)
- [Snowflake destination](https://dlthub.com/docs/dlt-ecosystem/destinations/snowflake)

## Prerequisites

- AWS account
- Terraform >= 1.x
- Docker (for building the ingest job image)
- Python 3.12+ with `uv` (for local development)
- Snowflake account (for destination)

## Project structure

- `terraform/` – AWS infrastructure (S3, ECS, EventBridge Scheduler, IAM for Secrets Manager)
- `ingest_job/` – Python job that reads config from S3 and runs dlt pipelines (Salesforce, HubSpot → Snowflake)
- `docs/` – Architecture and runbooks

## Quick start

1. Copy `.env.example` to `.env` and set variables (including `ecs_subnet_ids` and `ecs_security_group_ids` for Fargate).
2. Build and push the ingest job image to ECR (see `ingest_job/README.md`).
3. Upload pipeline configs to the S3 config bucket (e.g. `aws s3 cp terraform/configs/tenants/ s3://<bucket>/tenants/ --recursive`).
4. From `terraform/`: `terraform init && terraform plan && terraform apply`.

## Adding a tenant

1. Add a YAML file under `terraform/configs/tenants/<tenant_id>/` (e.g. `salesforce.yaml`, `hubspot.yaml`). Include `pipeline_name`, `schedule` (5-field cron, e.g. `0 6 * * *`), `source`, and `destination` with `credentials_ref` pointing to Secrets Manager.
2. Run `terraform apply` so EventBridge Scheduler creates a schedule for the new config.
3. Upload the new config to S3: `aws s3 cp terraform/configs/tenants/<tenant_id>/<file>.yaml s3://<config-bucket>/tenants/<tenant_id>/`.
4. Create the required secrets in AWS Secrets Manager (Salesforce: `user_name`, `password`, `security_token`; HubSpot: `access_token` or `api_key`; Snowflake: connection credentials) and reference them in the config.
