"""Salesforce source helpers. From dlt-hub/verified-sources (sources/salesforce/helpers/records.py)."""

import pendulum
from typing import Optional, Iterable, Dict, Set, Any, cast

from simple_salesforce.exceptions import SalesforceMalformedRequest
from simple_salesforce import Salesforce
from dlt.common.typing import TDataItem

from ..settings import IS_PRODUCTION


def _process_record(
    record: Dict[str, Any], date_fields: Set[str], api_type: str
) -> Dict[str, Any]:
    """Process a single Salesforce record: remove attributes, normalize date fields."""
    record.pop("attributes", None)
    for field in date_fields:
        if record.get(field):
            if api_type == "bulk":
                record[field] = pendulum.from_timestamp(
                    record[field] / 1000,
                ).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            else:
                dt = cast(pendulum.DateTime, pendulum.parse(record[field]))
                record[field] = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return record


def get_records(
    sf: Salesforce,
    sobject: str,
    last_state: Optional[str] = None,
    replication_key: Optional[str] = None,
) -> Iterable[TDataItem]:
    """Retrieve records from Salesforce for the given sObject."""
    desc = getattr(sf, sobject).describe()
    compound_fields = {
        f["compoundFieldName"]
        for f in desc["fields"]
        if f["compoundFieldName"] is not None
    } - {"Name"}
    date_fields = {
        f["name"] for f in desc["fields"]
        if f["type"] == "datetime" and f["name"]
    }
    fields = [f["name"] for f in desc["fields"] if f["name"] not in compound_fields]

    predicate, order_by = "", ""
    if replication_key and last_state:
        predicate = f"WHERE {replication_key} > {last_state}"
        order_by = f"ORDER BY {replication_key} ASC"
    query = f"SELECT {', '.join(fields)} FROM {sobject} {predicate} {order_by}"
    if not IS_PRODUCTION:
        query += " LIMIT 100"

    try:
        for page in getattr(sf.bulk, sobject).query_all(query, lazy_operation=True):
            processed = [
                _process_record(record, date_fields, api_type="bulk") for record in page
            ]
            yield from processed
    except SalesforceMalformedRequest as e:
        if "FeatureNotEnabled" in str(e) or "Async API not enabled" in str(e):
            result = sf.query(query)
            while True:
                for record in result["records"]:
                    yield _process_record(
                        record, date_fields, api_type="standard"
                    )
                if result["done"]:
                    break
                result = sf.query_more(result["nextRecordsUrl"])
        else:
            raise
