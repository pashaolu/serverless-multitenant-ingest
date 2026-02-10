# Ingest job

Python job run as an ECS Fargate task. Reads pipeline config from S3 (`CONFIG_KEY`) and runs the configured **dlt** pipeline (Salesforce or HubSpot → Snowflake). Credentials for CRM and Snowflake are read from AWS Secrets Manager (see config `credentials_ref`).

## Local run (optional)

```bash
export S3_CONFIG_BUCKET=your-bucket
export CONFIG_KEY=tenants/example/salesforce.yaml
# AWS credentials in env or ~/.aws (for S3 and Secrets Manager)
uv sync && uv run python src/main.py
```

Create the secrets in AWS Secrets Manager (JSON) and upload the matching config YAML to S3. Example configs: `terraform/configs/tenants/example/salesforce.yaml`, `terraform/configs/tenants/example/hubspot.yaml`.

## Build and push (ECR)

From repo root, after creating an ECR repo and logging in:

```bash
docker build --platform linux/amd64 -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/mt-ingest:latest ingest_job/
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/mt-ingest:latest
```

Then set `TF_VAR_ingest_job_image` to that URI and run `terraform apply`.
