"""Resolve pipeline source from config: salesforce, hubspot. Returns a dlt source to run."""

from typing import Any, Dict

from sources.salesforce import salesforce_source
from sources.salesforce.helpers.client import SecurityTokenAuth
from secrets_resolver import (
    salesforce_credentials_from_secret,
    hubspot_credentials_from_secret,
)


def get_salesforce_source(source_config: Dict[str, Any]):
    """Build the Salesforce dlt source from config. Credentials from Secrets Manager."""
    credentials_ref = source_config.get("credentials_ref")
    if not credentials_ref:
        raise ValueError("source.credentials_ref is required for Salesforce")
    creds = salesforce_credentials_from_secret(credentials_ref)
    auth = SecurityTokenAuth(
        user_name=creds["user_name"],
        password=creds["password"],
        security_token=creds["security_token"],
    )
    return salesforce_source(credentials=auth)


def get_hubspot_source(source_config: Dict[str, Any]):
    """Build the HubSpot dlt source from config. Credentials from Secrets Manager."""
    from vendored.hubspot import hubspot

    credentials_ref = source_config.get("credentials_ref")
    if not credentials_ref:
        raise ValueError("source.credentials_ref is required for HubSpot")
    creds = hubspot_credentials_from_secret(credentials_ref)
    kwargs = {"api_key": creds["api_key"]}
    if source_config.get("include_history") is not None:
        kwargs["include_history"] = source_config["include_history"]
    if source_config.get("soft_delete") is not None:
        kwargs["soft_delete"] = source_config["soft_delete"]
    if source_config.get("include_custom_props") is not None:
        kwargs["include_custom_props"] = source_config["include_custom_props"]
    if source_config.get("properties"):
        kwargs["properties"] = source_config["properties"]
    return hubspot(**kwargs)


def pipeline_source_from_config(source_type: str, source_config: Dict[str, Any]):
    """
    Return a dlt source (callable that returns resources) for the given type and config.
    """
    if source_type == "salesforce":
        return get_salesforce_source(source_config)
    if source_type == "hubspot":
        return get_hubspot_source(source_config)
    raise ValueError(f"Unknown source type: {source_type}")


def run_pipeline(
    pipeline_name: str,
    destination_config: Dict[str, Any],
    source,
):
    """
    Build a dlt pipeline (Snowflake destination) and run the given source.
    destination_config: database, schema, credentials_ref, optional warehouse, role, dataset_name.
    """
    import os
    import dlt
    from secrets_resolver import get_secret

    dest = destination_config
    creds_ref = dest.get("credentials_ref")
    if not creds_ref:
        raise ValueError("destination.credentials_ref is required for Snowflake")
    sf_creds = get_secret(creds_ref)

    # dlt Snowflake destination reads from env; set so it finds credentials
    for key, value in sf_creds.items():
        if value is not None:
            env_key = f"DESTINATION__SNOWFLAKE__CREDENTIALS__{key}"
            os.environ[env_key] = str(value)
    if dest.get("database"):
        os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__database"] = dest["database"]
    if dest.get("schema"):
        os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__schema"] = dest["schema"]
    if dest.get("warehouse"):
        os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__warehouse"] = dest["warehouse"]
    if dest.get("role"):
        os.environ["DESTINATION__SNOWFLAKE__CREDENTIALS__role"] = dest["role"]

    pipeline = dlt.pipeline(
        pipeline_name=pipeline_name,
        destination="snowflake",
        dataset_name=dest.get("dataset_name") or pipeline_name,
    )
    load_info = pipeline.run(source)
    return load_info
