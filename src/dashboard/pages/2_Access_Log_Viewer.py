"""
Access Log Viewer page (SCRUM-49).

Lets you browse and filter raw access_log entries by IP address and username.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pandas as pd
import streamlit as st

from db.db_connection import get_connection

st.title("Access Log Viewer")


@st.cache_data(ttl=30)
def load_logs():
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM access_log")
        rows = cursor.fetchall()
        cursor.close()
    df = pd.DataFrame(rows)
    if not df.empty:
        # Sort by the first column (assumed to be the auto-increment
        # primary key) so the newest rows show first, without hardcoding
        # its exact name.
        pk_col = df.columns[0]
        df = df.sort_values(pk_col, ascending=False)
    return df


logs_df = load_logs()

if logs_df.empty:
    st.info("No access_log entries found yet.")
else:
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        ip_filter = st.text_input("Filter by IP address")
    with col2:
        user_filter = st.text_input("Filter by username")
    with col3:
        st.write("")
        st.write("")
        if st.button("Refresh"):
            st.cache_data.clear()
            st.rerun()

    filtered_df = logs_df.copy()

    if ip_filter and "ip_address" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["ip_address"].astype(str).str.contains(ip_filter, case=False, na=False)
        ]

    if user_filter and "username" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["username"].astype(str).str.contains(user_filter, case=False, na=False)
        ]

    st.caption(f"Showing {len(filtered_df)} of {len(logs_df)} rows.")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)