# Architecture

All AWS resources are provisioned with **Terraform** (S3, ECS, EventBridge Scheduler, IAM). High-level flow: EventBridge Scheduler triggers one ECS Fargate task per pipeline config. The task reads the YAML from S3, loads source and destination credentials from Secrets Manager, runs the dlt pipeline (any [dlt-supported source](https://dlthub.com/docs/dlt-ecosystem/verified-sources) → Snowflake), and exits. See the [README](../README.md) for the diagram and deploy/runbook.

## Components

| Component | Role |
|-----------|------|
| **Terraform** | Defines and deploys S3 bucket, ECS cluster and task definition, EventBridge schedules (one per config file), IAM roles and policies. |
| **S3** | Stores pipeline configs (one YAML per tenant/source). Key format: `tenants/<tenant_id>/<source>.yaml`. |
| **EventBridge Scheduler** | One schedule per config file; cron from YAML. Invokes ECS RunTask with `CONFIG_KEY` override. |
| **ECS Fargate** | Runs the ingest job container. Task role: S3 GetObject, Secrets Manager GetSecretValue. |
| **Secrets Manager** | Source and destination credentials (e.g. Salesforce, HubSpot, Snowflake); referenced by name in config `credentials_ref`. |
| **Ingest job** | Python: load config from S3, resolve source via `pipeline_sources` (any dlt source), run dlt pipeline to Snowflake. |

## Data flow

1. Scheduler fires → ECS RunTask with `CONFIG_KEY=tenants/acme/salesforce.yaml`.
2. Container starts → reads `S3_CONFIG_BUCKET` + `CONFIG_KEY` from env, fetches YAML from S3.
3. Parses config → `source.type`, `source.credentials_ref`, `destination.credentials_ref`.
4. Fetches secrets from Secrets Manager, builds dlt source (e.g. Salesforce, HubSpot, or any supported source) and pipeline (Snowflake).
5. `pipeline.run(source)` → extract from source, load into Snowflake; then process exits.
