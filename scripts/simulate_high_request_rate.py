"""
Simulate a controlled high request rate against the authorised lab API.

This script must only target the Ubuntu VM inside the private
VirtualBox Host-only network.
"""

import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests


API_URL = "http://localhost:5001/"
REQUEST_COUNT = 30
INTERVAL_SECONDS = 0.2
REQUEST_TIMEOUT_SECONDS = 5

ALLOWED_TARGETS = {
    "192.168.56.10",
    "127.0.0.1",
    "localhost",
}


def validate_target():
    """Prevent the script from targeting systems outside the lab."""

    hostname = urlparse(API_URL).hostname

    if hostname not in ALLOWED_TARGETS:
        raise ValueError(
            f"Target {hostname} is not an authorised lab address."
        )


def simulate_high_request_rate():
    """Send multiple API requests at a controlled high rate."""

    validate_target()

    successful_requests = 0
    failed_requests = 0
    response_times = []

    print("Starting controlled high-request-rate simulation")
    print(f"Target: {API_URL}")
    print(f"Requests: {REQUEST_COUNT}")
    print(f"Interval: {INTERVAL_SECONDS} seconds")
    print()

    simulation_start = time.perf_counter()

    with requests.Session() as session:
        session.headers.update(
            {"User-Agent": "PSM-High-Rate-Simulator/1.0"}
        )

        for request_number in range(1, REQUEST_COUNT + 1):
            timestamp = datetime.now(timezone.utc).isoformat()

            try:
                request_start = time.perf_counter()

                response = session.get(
                    API_URL,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )

                response_time_ms = (
                    time.perf_counter() - request_start
                ) * 1000

                response_times.append(response_time_ms)

                print(
                    f"[{request_number}/{REQUEST_COUNT}] "
                    f"{timestamp} "
                    f"status={response.status_code} "
                    f"response_time={response_time_ms:.2f}ms"
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
                    f"request_failed={error}"
                )

            if request_number < REQUEST_COUNT:
                time.sleep(INTERVAL_SECONDS)

    total_time = time.perf_counter() - simulation_start
    actual_rate = REQUEST_COUNT / total_time

    if response_times:
        average_response_time = sum(response_times) / len(response_times)
    else:
        average_response_time = 0

    print()
    print("High-request-rate simulation completed")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Actual rate: {actual_rate:.2f} requests/second")
    print(f"Average response time: {average_response_time:.2f}ms")


if __name__ == "__main__":
    simulate_high_request_rate()
