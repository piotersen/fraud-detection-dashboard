import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")

st.title("📊 Fraud Detection Dashboard")

# Auto-refresh co 1 sekundę (pełne odświeżenie strony)
st.markdown(
    """
    <meta http-equiv="refresh" content="1">
    """,
    unsafe_allow_html=True
)

# Load the alerts log CSV
df = pd.read_csv("alerts_log.csv")
df["Timestamp"] = pd.to_datetime(df["Timestamp"]).apply(lambda x: x.to_pydatetime())

# Sidebar filters
st.sidebar.header("Filters")

# Konwersja Timestamp -> datetime.datetime
min_time = df['Timestamp'].min().to_pydatetime()
max_time = df['Timestamp'].max().to_pydatetime()

# Ustawienie zakresu suwaka
start_date, end_date = st.sidebar.slider(
    "Select Time Range:",
    min_value=min_time,
    max_value=max_time,
    value=(min_time, max_time),
    format="YYYY-MM-DD HH:mm:ss"
)

# Filtrowanie danych
filtered_df = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]

# Optional filter by User_ID and Status
user_filter = st.sidebar.text_input("Filter by User ID (optional):")
status_filter = st.sidebar.selectbox("Select Status:", ["All", "FRAUD", "LEGIT"])

if user_filter:
    filtered_df = filtered_df[filtered_df["User_ID"].str.contains(user_filter)]
if status_filter != "All":
    filtered_df = filtered_df[filtered_df["Status"] == status_filter]

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Transactions", len(filtered_df))
col2.metric("Fraudulent", (filtered_df["Status"] == "FRAUD").sum())
col3.metric("Legitimate", (filtered_df["Status"] == "LEGIT").sum())

# Line chart
st.subheader("📈 Transactions Over Time")
time_chart = filtered_df.groupby(filtered_df["Timestamp"].dt.strftime("%H:%M:%S")).size().reset_index(name='count')
st.line_chart(time_chart.rename(columns={"Timestamp": "index"}).set_index("index"))

# Pie chart
st.subheader("🧾 Fraud vs Legitimate - Pie Chart")
st.plotly_chart(px.pie(filtered_df, names="Status", title="Fraud Ratio"), use_container_width=True)

# Data table
st.subheader("📋 Detailed Transactions")
st.dataframe(filtered_df.sort_values(by="Timestamp", ascending=False), use_container_width=True)

# Export to CSV
csv_export = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Data as CSV",
    data=csv_export,
    file_name="filtered_fraud_log.csv",
    mime="text/csv",
)
