"""
Extract security-relevant features from the access_log table.

For each combination of (ip_address, 1-minute time window), this computes:
  - request_count          : how many requests came from that IP in that minute
  - failed_login_count     : how many of those were failed logins
  - failed_login_ratio     : failed_login_count / request_count
  - distinct_paths         : how many different endpoints were hit
  - avg_response_time_ms   : average response time in that window
  - is_high_rate           : True if request_count exceeds HIGH_RATE_THRESHOLD
  - is_brute_force_suspect : True if failed logins look like a brute-force attempt

Run with:
    python scripts/extract_features.py
"""

import os
import sys
from collections import defaultdict

# Make "from db.db_connection import get_connection" work when this script
# is run from the project root (scripts/ is a sibling of src/).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from db.db_connection import get_connection  # noqa: E402


HIGH_RATE_THRESHOLD = 10            # requests per minute from one IP
FAILED_LOGIN_RATIO_THRESHOLD = 0.5  # 50% or more failed logins
BULK_ACCESS_RECORD_THRESHOLD = 1000 # total records returned per minute from on IP


def fetch_access_logs():
    """Pull every access_log row we need, oldest first."""
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT log_id, ip_address, action, method, path,
                   status_code, response_time_ms, records_returned, created_at
            FROM access_log
            ORDER BY created_at ASC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return rows


def bucket_key(ip_address, created_at):
    """Group logs by (ip, minute) so we can compute per-minute features."""
    minute_bucket = created_at.replace(second=0, microsecond=0)
    return (ip_address, minute_bucket)


def extract_features(rows):
    """Turn raw log rows into one feature dict per (ip, minute) bucket."""
    buckets = defaultdict(list)

    for row in rows:
        if row["created_at"] is None or row["ip_address"] is None:
            continue
        key = bucket_key(row["ip_address"], row["created_at"])
        buckets[key].append(row)

    features = []

    for (ip_address, minute_bucket), bucket_rows in sorted(
        buckets.items(), key=lambda item: item[0][1]
    ):
        request_count = len(bucket_rows)

        failed_logins = [r for r in bucket_rows if r["action"] == "login_failed"]
        failed_login_count = len(failed_logins)
        failed_login_ratio = (
            failed_login_count / request_count if request_count else 0
        )

        distinct_paths = len(
            {r["path"] for r in bucket_rows if r["path"] is not None}
        )

        response_times = [
            r["response_time_ms"]
            for r in bucket_rows
            if r["response_time_ms"] is not None
        ]
        avg_response_time_ms = (
            sum(response_times) / len(response_times) if response_times else None
        )

        records_returned_values = [
            r["records_returned"]
            for r in bucket_rows
            if r["records_returned"] is not None
        ]
        total_records_returned = sum(records_returned_values)

        features.append(
            {
                "ip_address": ip_address,
                "window_start": minute_bucket,
                "request_count": request_count,
                "failed_login_count": failed_login_count,
                "failed_login_ratio": round(failed_login_ratio, 2),
                "distinct_paths": distinct_paths,
                "avg_response_time_ms": (
                    round(avg_response_time_ms, 2)
                    if avg_response_time_ms is not None
                    else None
                ),
                "is_high_rate": request_count >= HIGH_RATE_THRESHOLD,
                "total_records_returned": total_records_returned,
                "is_bulk_access_suspect": total_records_returned >= BULK_ACCESS_RECORD_THRESHOLD,
                "is_brute_force_suspect": (
                    failed_login_count >= 3
                    and failed_login_ratio >= FAILED_LOGIN_RATIO_THRESHOLD
                ),
            }
        )

    return features


def print_features(features):
    print(
        f"{'IP':<15} {'Window Start':<20} {'Reqs':<5} {'Failed':<7} "
        f"{'FailRatio':<10} {'Paths':<6} {'AvgMs':<8} {'HighRate':<9} "
        f"{'TotalRecs':<10} {'BulkAccess?':<12} {'BruteForce?'}"
    )
    print("-" * 130)
    for f in features:
        print(
            f"{f['ip_address']:<15} "
            f"{f['window_start'].strftime('%Y-%m-%d %H:%M'):<20} "
            f"{f['request_count']:<5} "
            f"{f['failed_login_count']:<7} "
            f"{f['failed_login_ratio']:<10} "
            f"{f['distinct_paths']:<6} "
            f"{str(f['avg_response_time_ms']):<8} "
            f"{str(f['is_high_rate']):<9} "
            f"{f['total_records_returned']:<10} "
            f"{str(f['is_bulk_access_suspect']):<12} "
            f"{f['is_brute_force_suspect']}"
        )

if __name__ == "__main__":
    rows = fetch_access_logs()
    print(f"Loaded {len(rows)} access_log rows.\n")

    features = extract_features(rows)
    print(f"Computed {len(features)} (ip, 1-minute window) feature rows.\n")

    print_features(features)