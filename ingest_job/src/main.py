"""
Ingest job entrypoint. Reads CONFIG_KEY from env, fetches YAML from S3, parses and logs.
Stage 1: stub only (no dlt run). Later stages will run the pipeline.
"""
import os
import sys

import boto3
import yaml


def get_config_from_s3(bucket: str, key: str) -> dict:
    """Fetch pipeline config YAML from S3 and return parsed dict."""
    client = boto3.client("s3")
    response = client.get_object(Bucket=bucket, Key=key)
    body = response["Body"].read().decode("utf-8")
    return yaml.safe_load(body)


def main() -> None:
    bucket = os.environ.get("S3_CONFIG_BUCKET")
    config_key = os.environ.get("CONFIG_KEY")

    if not bucket or not config_key:
        print("Missing S3_CONFIG_BUCKET or CONFIG_KEY", file=sys.stderr)
        sys.exit(1)

    config = get_config_from_s3(bucket, config_key)
    print("Config loaded:", config_key)
    print("Pipeline name:", config.get("pipeline_name", "(none)"))
    print("Tenant ID:", config.get("tenant_id", "(none)"))
    if "source" in config:
        print("Source type:", config["source"].get("type", "(none)"))
    if "destination" in config:
        print("Destination type:", config["destination"].get("type", "(none)"))


if __name__ == "__main__":
    main()
