# Architecture

High-level flow: EventBridge Scheduler triggers one ECS Fargate task per pipeline config. The task reads the YAML from S3, loads CRM and Snowflake credentials from Secrets Manager, runs the dlt pipeline (Salesforce or HubSpot → Snowflake), and exits. See the [README](../README.md) for the diagram and deploy/runbook.

## Components

| Component | Role |
|-----------|------|
| **S3** | Stores pipeline configs (one YAML per tenant/source). Key format: `tenants/<tenant_id>/<source>.yaml`. |
| **EventBridge Scheduler** | One schedule per config file; cron from YAML. Invokes ECS RunTask with `CONFIG_KEY` override. |
| **ECS Fargate** | Runs the ingest job container. Task role: S3 GetObject, Secrets Manager GetSecretValue. |
| **Secrets Manager** | CRM (Salesforce/HubSpot) and Snowflake credentials; referenced by name in config `credentials_ref`. |
| **Ingest job** | Python: load config from S3, resolve source via `pipeline_sources`, run dlt pipeline to Snowflake. |

## Data flow

1. Scheduler fires → ECS RunTask with `CONFIG_KEY=tenants/acme/salesforce.yaml`.
2. Container starts → reads `S3_CONFIG_BUCKET` + `CONFIG_KEY` from env, fetches YAML from S3.
3. Parses config → `source.type`, `source.credentials_ref`, `destination.credentials_ref`.
4. Fetches secrets from Secrets Manager, builds dlt source (Salesforce or HubSpot) and pipeline (Snowflake).
5. `pipeline.run(source)` → extract from CRM, load into Snowflake; then process exits.
