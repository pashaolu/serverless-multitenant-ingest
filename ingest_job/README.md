# Ingest job

Python job run as an ECS Fargate task. Reads pipeline config from S3 (`CONFIG_KEY`) and runs the configured dlt pipeline (Stage 2+). Stage 1 only loads and logs the config.

## Local run (optional)

```bash
export S3_CONFIG_BUCKET=your-bucket
export CONFIG_KEY=tenants/example/salesforce.yaml
# AWS credentials in env or ~/.aws
uv sync && uv run python src/main.py
```

## Build and push (ECR)

From repo root, after creating an ECR repo and logging in:

```bash
docker build --platform linux/amd64 -t ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/mt-ingest:latest ingest_job/
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/mt-ingest:latest
```

Then set `TF_VAR_ingest_job_image` to that URI and run `terraform apply`.
