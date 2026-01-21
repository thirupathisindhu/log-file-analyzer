import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="IT Operations Log Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- SIMPLE LOGIN --------------------
def login():
    st.title("🔐 Login")
    st.write("Enter credentials to access the dashboard")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

if "logged_in" not in st.session_state:
    login()
    st.stop()

# -------------------- SIDEBAR --------------------
st.sidebar.title("⚙ Dashboard Settings")

show_4xx = st.sidebar.checkbox("Show 4xx Errors", True)
show_5xx = st.sidebar.checkbox("Show 5xx Errors", True)

uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Log File (CSV)",
    type=["csv"]
)

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# -------------------- LOAD DATA --------------------
if uploaded_file:
    df_raw = pd.read_csv(uploaded_file)
else:
    df_raw = pd.read_csv("logs/server_logs.csv")

valid_rows = []
invalid_lines = 0

for _, row in df_raw.iterrows():
    try:
        valid_rows.append([
            row["timestamp"],
            row["ip"],
            row["request"],
            int(row["error_code"])
        ])
    except:
        invalid_lines += 1

df = pd.DataFrame(
    valid_rows,
    columns=["timestamp", "ip", "request", "error_code"]
)

total_requests = len(df)
total_errors = df[df["error_code"] >= 400].shape[0]

# -------------------- HEADER --------------------
st.title("🖥 IT Operations Log File Analyzer")
st.caption("Enterprise-style log monitoring dashboard using Python & Streamlit")

# -------------------- METRICS --------------------
c1, c2, c3 = st.columns(3)

c1.metric("📄 Total Requests", total_requests)
c2.metric("❌ Total Errors", total_errors)
c3.metric("⚠ Invalid Log Lines", invalid_lines)

st.divider()

# -------------------- FILTER ERRORS --------------------
error_df = df[df["error_code"] >= 400]

if not show_4xx:
    error_df = error_df[~error_df["error_code"].between(400, 499)]

if not show_5xx:
    error_df = error_df[~error_df["error_code"].between(500, 599)]

# -------------------- CHARTS --------------------
left, right = st.columns(2)

# ---- Error Code Distribution ----
with left:
    st.subheader("📊 HTTP Error Code Distribution")
    st.caption("Shows frequency of different HTTP error codes")

    error_counts = error_df["error_code"].value_counts()

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(error_counts.index.astype(str), error_counts.values)
    ax.set_xlabel("Error Code")
    ax.set_ylabel("Count")
    st.pyplot(fig)

# ---- Top IPs ----
with right:
    st.subheader("🌐 Top 5 IPs Generating Errors")
    st.caption("Identifies IP addresses causing maximum failures")

    ip_counts = error_df["ip"].value_counts().head(5)

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(ip_counts.index, ip_counts.values)
    ax.set_xlabel("IP Address")
    ax.set_ylabel("Error Count")
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.divider()

# -------------------- REQUEST TYPE DISTRIBUTION --------------------
st.subheader("🔄 Request Type Distribution")
st.caption("Breakdown of HTTP request methods")

req_counts = df["request"].value_counts()

fig, ax = plt.subplots(figsize=(5, 3))
ax.bar(req_counts.index, req_counts.values, color="green")
ax.set_xlabel("Request Type")
ax.set_ylabel("Count")
st.pyplot(fig)

# -------------------- LATEST ERRORS TABLE --------------------
st.divider()
st.subheader("📋 Recent Error Events")
st.caption("Latest 10 error entries from logs")

st.dataframe(
    error_df.sort_values("timestamp", ascending=False).head(10),
    use_container_width=True
)

# -------------------- HEALTH STATUS --------------------
st.divider()
error_rate = (total_errors / total_requests) * 100 if total_requests else 0

st.subheader("🩺 System Health Status")

if error_rate < 10:
    st.success(f"System Healthy 🟢 (Error Rate: {error_rate:.1f}%)")
elif error_rate < 30:
    st.warning(f"System Warning 🟡 (Error Rate: {error_rate:.1f}%)")
else:
    st.error(f"System Critical 🔴 (Error Rate: {error_rate:.1f}%)")
