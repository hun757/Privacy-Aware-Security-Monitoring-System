"""
Security Overview page (SCRUM-48).

Shows summary cards and a table of recent alerts from the security_alerts
table (populated by scripts/generate_alerts.py).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pandas as pd
import streamlit as st

from db.db_connection import get_connection

st.title("Security Overview")


@st.cache_data(ttl=30)
def load_alerts():
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT alert_id, alert_type, ip_address, window_start, "
            "details, severity, created_at "
            "FROM security_alerts "
            "ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
        cursor.close()
    return pd.DataFrame(rows)


alerts_df = load_alerts()

if alerts_df.empty:
    st.info(
        "No alerts have been generated yet. Run "
        "`python scripts/generate_alerts.py` first, then refresh this page."
    )
else:
    total = len(alerts_df)
    high = int((alerts_df["severity"] == "high").sum())
    medium = int((alerts_df["severity"] == "medium").sum())
    low = int((alerts_df["severity"] == "low").sum())

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Alerts", total)
    col2.metric("High Severity", high)
    col3.metric("Medium Severity", medium)
    col4.metric("Low Severity", low)

    st.subheader("Recent Alerts")
    st.dataframe(
        alerts_df.sort_values("created_at", ascending=False).head(50),
        use_container_width=True,
        hide_index=True,
    )

    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()