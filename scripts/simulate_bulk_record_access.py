"""
Simulate repeated bulk access to protected records.

This script must only target the authorised Ubuntu VM inside the
private VirtualBox Host-only lab network.

The endpoint path may need to be updated after the team finalises
the protected-data API.
"""

import os
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests


API_URL = "http://localhost:5001/protected-data"
REQUEST_COUNT = 5
RECORDS_PER_REQUEST = 500
DELAY_SECONDS = 2
REQUEST_TIMEOUT_SECONDS = 10

ALLOWED_TARGETS = {
    "192.168.56.10",
    "127.0.0.1",
    "localhost",
}


def validate_target():
    """Prevent requests to systems outside the authorised lab."""

    hostname = urlparse(API_URL).hostname

    if hostname not in ALLOWED_TARGETS:
        raise ValueError(
            f"Target {hostname} is not an authorised lab address."
        )


def count_returned_records(response):
    """Count records from common JSON response formats."""

    try:
        response_data = response.json()
    except ValueError:
        return 0

    if isinstance(response_data, list):
        return len(response_data)

    if isinstance(response_data, dict):
        records = response_data.get("records", [])

        if isinstance(records, list):
            return len(records)

    return 0


def simulate_bulk_record_access():
    """Repeatedly request large batches of protected records."""

    validate_target()

    api_token = os.getenv("API_TOKEN")

    successful_requests = 0
    failed_requests = 0
    total_records_received = 0

    print("Starting bulk-record-access simulation")
    print(f"Target: {API_URL}")
    print(f"Requests: {REQUEST_COUNT}")
    print(f"Records requested each time: {RECORDS_PER_REQUEST}")
    print()

    with requests.Session() as session:
        session.headers.update(
            {"User-Agent": "PSM-Bulk-Access-Simulator/1.0"}
        )

        if api_token:
            session.headers.update(
                {"Authorization": f"Bearer {api_token}"}
            )

        for request_number in range(1, REQUEST_COUNT + 1):
            timestamp = datetime.now(timezone.utc).isoformat()

            try:
                response = session.get(
                    API_URL,
                    params={
                        "limit": RECORDS_PER_REQUEST,
                        "offset": 0,
                    },
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )

                returned_records = count_returned_records(response)
                total_records_received += returned_records

                print(
                    f"[{request_number}/{REQUEST_COUNT}] "
                    f"{timestamp} "
                    f"GET /protected-data "
                    f"requested={RECORDS_PER_REQUEST} "
                    f"returned={returned_records} "
                    f"status={response.status_code}"
                )

                if response.ok:
                    successful_requests += 1
                else:
                    failed_requests += 1

            except requests.RequestException as error:
                failed_requests += 1

                print(
                    f"[{request_number}/{REQUEST_COUNT}] "
                    f"{timestamp} "
                    f"connection_error={error}"
                )

            if request_number < REQUEST_COUNT:
                time.sleep(DELAY_SECONDS)

    print()
    print("Bulk-record-access simulation completed")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Total records received: {total_records_received}")


if __name__ == "__main__":
    simulate_bulk_record_access()
