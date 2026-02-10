"""Resolve credentials from AWS Secrets Manager. Config references by secret name or ARN."""

import json
import os
from typing import Any, Dict

import boto3


def get_secret(secret_ref: str) -> Dict[str, Any]:
    """
    Fetch a secret from AWS Secrets Manager.
    secret_ref: either a secret name (e.g. 'acme/salesforce') or full ARN.
    Returns the secret as a dict (expects JSON secret value).
    """
    client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    try:
        response = client.get_secret_value(SecretId=secret_ref)
    except client.exceptions.ResourceNotFoundException:
        raise ValueError(f"Secret not found: {secret_ref}")
    value = response.get("SecretString")
    if not value:
        raise ValueError(f"Secret has no string value: {secret_ref}")
    return json.loads(value)


def salesforce_credentials_from_secret(secret_ref: str) -> Dict[str, Any]:
    """
    Load Salesforce credentials from Secrets Manager.
    Expected JSON keys: user_name, password, security_token (for SecurityTokenAuth).
    """
    data = get_secret(secret_ref)
    return {
        "user_name": data.get("user_name"),
        "password": data.get("password"),
        "security_token": data.get("security_token"),
    }


def hubspot_credentials_from_secret(secret_ref: str) -> Dict[str, Any]:
    """
    Load HubSpot credentials from Secrets Manager.
    Expected JSON key: access_token or api_key (private app access token).
    """
    data = get_secret(secret_ref)
    token = data.get("access_token") or data.get("api_key")
    if not token:
        raise ValueError("HubSpot secret must contain 'access_token' or 'api_key'")
    return {"api_key": token}


def snowflake_credentials_from_secret(secret_ref: str) -> Dict[str, Any]:
    """
    Load Snowflake credentials from Secrets Manager.
    Expected JSON keys: database, username, password, host, warehouse, role (optional).
    """
    return get_secret(secret_ref)
