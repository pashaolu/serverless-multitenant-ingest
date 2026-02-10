"""
Ingest job entrypoint. Reads CONFIG_KEY from env, fetches YAML from S3, runs the
config-driven dlt pipeline (Salesforce/HubSpot -> Snowflake). Credentials from
AWS Secrets Manager.
"""
import logging
import os
import sys

import boto3
import yaml

from pipeline_sources import pipeline_source_from_config, run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log = logging.getLogger(__name__)


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
        log.error("Missing S3_CONFIG_BUCKET or CONFIG_KEY")
        sys.exit(1)

    config = get_config_from_s3(bucket, config_key)
    pipeline_name = config.get("pipeline_name") or config_key.replace("/", "_").replace(".yaml", "")
    source_cfg = config.get("source", {})
    dest_cfg = config.get("destination", {})

    if not source_cfg or not dest_cfg:
        log.error("Config must include 'source' and 'destination'")
        sys.exit(1)

    source_type = source_cfg.get("type")
    if not source_type:
        log.error("source.type is required")
        sys.exit(1)

    try:
        source = pipeline_source_from_config(source_type, source_cfg)
    except ValueError as e:
        log.error("Source error: %s", e)
        sys.exit(1)

    if dest_cfg.get("type") != "snowflake":
        log.error("Only destination type 'snowflake' is supported")
        sys.exit(1)

    try:
        load_info = run_pipeline(pipeline_name, dest_cfg, source)
        log.info("Pipeline completed: %s", load_info)
    except Exception as e:
        log.exception("Pipeline run failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
