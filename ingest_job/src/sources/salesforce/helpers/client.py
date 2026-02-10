"""Salesforce API client helpers. From dlt-hub/verified-sources (sources/salesforce/helpers/client.py)."""

from typing import Optional, Union, cast
import json

from dlt.sources.helpers.requests import Session
from simple_salesforce import Salesforce
from simple_salesforce.util import Proxies
from simple_salesforce.api import DEFAULT_API_VERSION
from dlt.common.typing import TSecretStrValue
from dlt.common.configuration.specs import (
    CredentialsConfiguration,
    configspec,
    BaseConfiguration,
)
from dlt.common.configuration import with_config
from dlt.common.configuration.exceptions import ConfigurationValueError


@configspec
class SalesforceClientConfiguration(BaseConfiguration):
    domain: Optional[str] = None
    version: Optional[str] = DEFAULT_API_VERSION
    proxies: Optional[str] = None
    client_id: Optional[str] = None

    def get_proxies(self) -> Optional[Proxies]:
        if self.proxies is None:
            return None
        return cast(Proxies, json.loads(self.proxies))


@configspec
class SalesforceCredentialsBase(CredentialsConfiguration):
    """Base for Salesforce credential types."""


@configspec
class SecurityTokenAuth(SalesforceCredentialsBase):
    """OAuth 2.0 Username Password Flow with security token."""

    user_name: str = None
    password: TSecretStrValue = None
    security_token: TSecretStrValue = None


@configspec
class OrganizationIdAuth(SalesforceCredentialsBase):
    """Credentials based on Trusted IP Ranges in Salesforce."""

    user_name: str = None
    password: TSecretStrValue = None
    organization_id: TSecretStrValue = None


@configspec
class InstanceAuth(SalesforceCredentialsBase):
    """Direct session access credentials."""

    session_id: str = None
    instance: Optional[TSecretStrValue] = None
    instance_url: Optional[TSecretStrValue] = None

    def on_resolved(self) -> None:
        if not self.instance and not self.instance_url:
            raise ConfigurationValueError(
                "InstanceAuth requires either 'instance' or 'instance_url'. "
                "Please provide one of these fields."
            )


@configspec
class ConsumerKeySecretAuth(SalesforceCredentialsBase):
    """OAuth 2.0 Username Password Flow with connected app."""

    user_name: str = None
    password: TSecretStrValue = None
    consumer_key: TSecretStrValue = None
    consumer_secret: TSecretStrValue = None


@configspec
class JWTAuth(SalesforceCredentialsBase):
    """OAuth 2.0 JWT Bearer Flow credentials."""

    user_name: str = None
    consumer_key: TSecretStrValue = None
    privatekey_file: Optional[TSecretStrValue] = None
    privatekey: Optional[TSecretStrValue] = None
    instance_url: Optional[TSecretStrValue] = None

    def on_resolved(self) -> None:
        if not self.privatekey_file and not self.privatekey:
            raise ConfigurationValueError(
                "JWTAuth requires either 'privatekey_file' or 'privatekey'. "
                "Please provide one of these fields."
            )


@configspec
class ConsumerKeySecretDomainAuth(SalesforceCredentialsBase):
    """OAuth 2.0 Client Credentials Flow."""

    consumer_key: TSecretStrValue = None
    consumer_secret: TSecretStrValue = None
    domain: str = None


SalesforceAuth = Union[
    SecurityTokenAuth,
    OrganizationIdAuth,
    ConsumerKeySecretAuth,
    JWTAuth,
    ConsumerKeySecretDomainAuth,
    InstanceAuth,
]


@with_config(spec=SalesforceClientConfiguration)
def make_salesforce_client(
    credentials: SalesforceAuth,
    session: Optional[Session] = None,
    config: SalesforceClientConfiguration = None,
) -> Salesforce:
    """Build a Salesforce client from the given credentials and config."""
    if isinstance(credentials, SecurityTokenAuth):
        return Salesforce(
            version=config.version,
            domain=config.domain,
            session=session,
            proxies=config.get_proxies(),
            username=credentials.user_name,
            password=credentials.password,
            security_token=credentials.security_token,
            client_id=config.client_id,
        )
    elif isinstance(credentials, InstanceAuth):
        return Salesforce(
            version=config.version,
            domain=config.domain,
            session=session,
            proxies=config.get_proxies(),
            session_id=credentials.session_id,
            instance=credentials.instance,
            instance_url=credentials.instance_url,
        )
    elif isinstance(credentials, OrganizationIdAuth):
        return Salesforce(
            version=config.version,
            domain=config.domain,
            session=session,
            proxies=config.get_proxies(),
            username=credentials.user_name,
            password=credentials.password,
            organizationId=credentials.organization_id,
            client_id=config.client_id,
        )
    elif isinstance(credentials, ConsumerKeySecretAuth):
        return Salesforce(
            version=config.version,
            domain=config.domain,
            session=session,
            proxies=config.get_proxies(),
            username=credentials.user_name,
            password=credentials.password,
            consumer_key=credentials.consumer_key,
            consumer_secret=credentials.consumer_secret,
        )
    elif isinstance(credentials, JWTAuth):
        return Salesforce(
            version=config.version,
            domain=config.domain,
            session=session,
            proxies=config.get_proxies(),
            username=credentials.user_name,
            instance_url=credentials.instance_url,
            consumer_key=credentials.consumer_key,
            privatekey_file=credentials.privatekey_file,
            privatekey=credentials.privatekey,
        )
    elif isinstance(credentials, ConsumerKeySecretDomainAuth):
        return Salesforce(
            version=config.version,
            session=session,
            proxies=config.get_proxies(),
            consumer_key=credentials.consumer_key,
            consumer_secret=credentials.consumer_secret,
            domain=credentials.domain,
        )
    else:
        raise TypeError("Provide a valid set of Salesforce credentials.")
