"""Salesforce dlt source. From dlt-hub/verified-sources (sources/salesforce)."""

from typing import Iterable, Optional

import dlt
from dlt.sources import DltResource
from dlt.sources import incremental
from dlt.sources.helpers.requests import Session
from dlt.common.typing import TDataItem

from .helpers.records import get_records
from .helpers.client import SalesforceAuth, make_salesforce_client


@dlt.source(name="salesforce")
def salesforce_source(
    credentials: SalesforceAuth = dlt.secrets.value,
    session: Optional[Session] = None,
) -> Iterable[DltResource]:
    """dlt source for Salesforce. Yields resources for User, Account, Contact, etc."""
    client = make_salesforce_client(credentials, session)

    @dlt.resource(write_disposition="replace")
    def sf_user() -> Iterable[TDataItem]:
        yield from get_records(client, "User")

    @dlt.resource(write_disposition="replace")
    def user_role() -> Iterable[TDataItem]:
        yield from get_records(client, "UserRole")

    @dlt.resource(write_disposition="merge")
    def opportunity(
        last_timestamp: incremental[str] = dlt.sources.incremental(
            "SystemModstamp", initial_value=None
        ),
    ) -> Iterable[TDataItem]:
        yield from get_records(
            client, "Opportunity", last_timestamp.last_value, "SystemModstamp"
        )

    @dlt.resource(write_disposition="merge")
    def opportunity_line_item(
        last_timestamp: incremental[str] = dlt.sources.incremental(
            "SystemModstamp", initial_value=None
        ),
    ) -> Iterable[TDataItem]:
        yield from get_records(
            client, "OpportunityLineItem", last_timestamp.last_value, "SystemModstamp"
        )

    @dlt.resource(write_disposition="merge")
    def opportunity_contact_role(
        last_timestamp: incremental[str] = dlt.sources.incremental(
            "SystemModstamp", initial_value=None
        ),
    ) -> Iterable[TDataItem]:
        yield from get_records(
            client,
            "OpportunityContactRole",
            last_timestamp.last_value,
            "SystemModstamp",
        )

    @dlt.resource(write_disposition="merge")
    def account(
        last_timestamp: incremental[str] = dlt.sources.incremental(
            "LastModifiedDate", initial_value=None
        ),
    ) -> Iterable[TDataItem]:
        yield from get_records(
            client, "Account", last_timestamp.last_value, "LastModifiedDate"
        )

    @dlt.resource(write_disposition="replace")
    def contact() -> Iterable[TDataItem]:
        yield from get_records(client, "Contact")

    @dlt.resource(write_disposition="replace")
    def lead() -> Iterable[TDataItem]:
        yield from get_records(client, "Lead")

    @dlt.resource(write_disposition="replace")
    def campaign() -> Iterable[TDataItem]:
        yield from get_records(client, "Campaign")

    @dlt.resource(write_disposition="merge")
    def campaign_member(
        last_timestamp: incremental[str] = dlt.sources.incremental(
            "SystemModstamp", initial_value=None
        ),
    ) -> Iterable[TDataItem]:
        yield from get_records(
            client, "CampaignMember", last_timestamp.last_value, "SystemModstamp"
        )

    @dlt.resource(write_disposition="replace")
    def product_2() -> Iterable[TDataItem]:
        yield from get_records(client, "Product2")

    @dlt.resource(write_disposition="replace")
    def pricebook_2() -> Iterable[TDataItem]:
        yield from get_records(client, "Pricebook2")

    @dlt.resource(write_disposition="replace")
    def pricebook_entry() -> Iterable[TDataItem]:
        yield from get_records(client, "PricebookEntry")

    @dlt.resource(write_disposition="merge")
    def task(
        last_timestamp: incremental[str] = dlt.sources.incremental(
            "SystemModstamp", initial_value=None
        ),
    ) -> Iterable[TDataItem]:
        yield from get_records(client, "Task", last_timestamp.last_value, "SystemModstamp")

    @dlt.resource(write_disposition="merge")
    def event(
        last_timestamp: incremental[str] = dlt.sources.incremental(
            "SystemModstamp", initial_value=None
        ),
    ) -> Iterable[TDataItem]:
        yield from get_records(client, "Event", last_timestamp.last_value, "SystemModstamp")

    return (
        sf_user,
        user_role,
        opportunity,
        opportunity_line_item,
        opportunity_contact_role,
        account,
        contact,
        lead,
        campaign,
        campaign_member,
        product_2,
        pricebook_2,
        pricebook_entry,
        task,
        event,
    )
