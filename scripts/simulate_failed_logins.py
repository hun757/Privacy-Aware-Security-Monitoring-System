"""
Simulate repeated failed login attempts against the authorised lab API.

This script uses a deliberately invalid password and must only target
the Ubuntu VM inside the controlled Host-only lab network.
"""

import time
from datetime import datetime, timezone

import requests


LOGIN_URL = "http://192.168.56.10:5001/login"
TEST_USERNAME = "lab_test_user"
INVALID_PASSWORD = "deliberately-wrong-password"
ATTEMPT_COUNT = 8
DELAY_SECONDS = 1
REQUEST_TIMEOUT_SECONDS = 5


def simulate_failed_logins():
    """Send repeated login requests using an invalid password."""

    expected_failures = 0
    unexpected_responses = 0
    connection_errors = 0

    print("Starting repeated failed-login simulation")
    print(f"Target: {LOGIN_URL}")
    print(f"Username: {TEST_USERNAME}")
    print(f"Attempts: {ATTEMPT_COUNT}")
    print()

    with requests.Session() as session:
        session.headers.update(
            {"User-Agent": "PSM-Failed-Login-Simulator/1.0"}
        )

        for attempt_number in range(1, ATTEMPT_COUNT + 1):
            timestamp = datetime.now(timezone.utc).isoformat()

            try:
                response = session.post(
                    LOGIN_URL,
                    json={
                        "username": TEST_USERNAME,
                        "password": INVALID_PASSWORD,
                    },
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )

                print(
                    f"[{attempt_number}/{ATTEMPT_COUNT}] "
                    f"{timestamp} "
                    f"POST /login "
                    f"status={response.status_code}"
                )

                if response.status_code == 401:
                    expected_failures += 1
                else:
                    unexpected_responses += 1

            except requests.RequestException as error:
                connection_errors += 1

                print(
                    f"[{attempt_number}/{ATTEMPT_COUNT}] "
                    f"{timestamp} "
                    f"connection_error={error}"
                )

            if attempt_number < ATTEMPT_COUNT:
                time.sleep(DELAY_SECONDS)

    print()
    print("Failed-login simulation completed")
    print(f"Expected 401 responses: {expected_failures}")
    print(f"Unexpected responses: {unexpected_responses}")
    print(f"Connection errors: {connection_errors}")


if __name__ == "__main__":
    simulate_failed_logins()
