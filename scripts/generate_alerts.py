"""
Generate security alerts from access_log features.

Reuses the feature-extraction logic from extract_features.py, then turns
any suspicious (ip, minute) window into a row in security_alerts.

Run with:
    python scripts/generate_alerts.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from db.db_connection import get_connection  # noqa: E402
from extract_features import fetch_access_logs, extract_features  # noqa: E402


def build_alerts(features):
    """Turn flagged feature rows into alert records."""
    alerts = []

    for f in features:
        if f["is_brute_force_suspect"]:
            alerts.append(
                {
                    "alert_type": "brute_force",
                    "ip_address": f["ip_address"],
                    "window_start": f["window_start"],
                    "details": (
                        f"{f['failed_login_count']} failed logins "
                        f"({f['failed_login_ratio'] * 100:.0f}% failure rate) in 1 minute"
                    ),
                    "severity": "high",
                }
            )

        if f["is_high_rate"]:
            alerts.append(
                {
                    "alert_type": "high_request_rate",
                    "ip_address": f["ip_address"],
                    "window_start": f["window_start"],
                    "details": f"{f['request_count']} requests in 1 minute",
                    "severity": "medium",
                }
            )

        if f["is_bulk_access_suspect"]:
            alerts.append(
                {
                    "alert_type": "bulk_access",
                    "ip_address": f["ip_address"],
                    "window_start": f["window_start"],
                    "details": (
                        f"{f['total_records_returned']} records returned in 1 minute"
                    ),
                    "severity": "high",
                }
            )

    return alerts


def save_alerts(alerts):
    """Insert alerts into security_alerts, skipping ones already stored."""
    inserted = 0

    with get_connection() as conn:
        cursor = conn.cursor()
        for alert in alerts:
            cursor.execute(
                "INSERT IGNORE INTO security_alerts "
                "(alert_type, ip_address, window_start, details, severity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (
                    alert["alert_type"],
                    alert["ip_address"],
                    alert["window_start"],
                    alert["details"],
                    alert["severity"],
                ),
            )
            inserted += cursor.rowcount
        conn.commit()
        cursor.close()

    return inserted


if __name__ == "__main__":
    rows = fetch_access_logs()
    print(f"Loaded {len(rows)} access_log rows.")

    features = extract_features(rows)
    print(f"Computed {len(features)} (ip, 1-minute window) feature rows.")

    alerts = build_alerts(features)
    print(f"Found {len(alerts)} suspicious windows.\n")

    for alert in alerts:
        print(
            f"[{alert['severity'].upper()}] {alert['alert_type']} — "
            f"{alert['ip_address']} at {alert['window_start']} — {alert['details']}"
        )

    new_count = save_alerts(alerts)
    print(f"\n{new_count} new alert(s) saved to security_alerts (duplicates skipped).")