"""
Generate low-rate normal traffic for the authorised lab API.

Target:
    Ubuntu Flask API on the VirtualBox Host-only network.

Example:
    python scripts/simulate_normal_traffic.py
"""

import random
import time
from datetime import datetime, timezone

import requests


API_URL = "http://localhost:5001/"
REQUEST_COUNT = 10
MIN_DELAY_SECONDS = 2
MAX_DELAY_SECONDS = 5
REQUEST_TIMEOUT_SECONDS = 5


def generate_normal_traffic():
    """Send low-rate GET requests that represent normal API access."""

    successful_requests = 0
    failed_requests = 0

    print("Starting normal access traffic simulation")
    print(f"Target: {API_URL}")
    print(f"Number of requests: {REQUEST_COUNT}")
    print()

    with requests.Session() as session:
        session.headers.update(
            {"User-Agent": "PSM-Normal-Traffic-Simulator/1.0"}
        )

        for request_number in range(1, REQUEST_COUNT + 1):
            timestamp = datetime.now(timezone.utc).isoformat()

            try:
                start_time = time.perf_counter()

                response = session.get(
                    API_URL,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )

                response_time_ms = (
                    time.perf_counter() - start_time
                ) * 1000

                print(
                    f"[{request_number}/{REQUEST_COUNT}] "
                    f"{timestamp} "
                    f"GET / "
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
                delay = random.uniform(
                    MIN_DELAY_SECONDS,
                    MAX_DELAY_SECONDS,
                )
                time.sleep(delay)

    print()
    print("Normal traffic simulation completed")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")


if __name__ == "__main__":
    generate_normal_traffic()
