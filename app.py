import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Fintech Dashboard", layout="wide")

# ---------- STYLING ----------
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1f2937, #111827);
    border-radius: 12px;
    padding: 15px;
}

.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

section[data-testid="stSidebar"] {
    background-color: #111827;
}

h1, h2, h3 { color: #00c6ff; }
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
conn = sqlite3.connect("finance.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
type TEXT,
category TEXT,
amount REAL,
date TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS goals (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user TEXT,
goal_name TEXT,
target REAL,
saved REAL
)
""")

conn.commit()

# ---------- HEADER ----------
st.title("💳 Premium Finance Analytics System")

# ---------- AUTH ----------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Create Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")

    if st.button("Register"):
        try:
            cur.execute("INSERT INTO users VALUES (NULL,?,?)",(new_user,new_pass))
            conn.commit()
            st.success("Account created!")
        except:
            st.error("User already exists")

if choice == "Login":
    st.subheader("Login")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        result = cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user,password)
        ).fetchone()

        if result:
            st.session_state.user = user
            st.success("Logged in!")

# ---------- DASHBOARD ----------
if "user" in st.session_state:

    st.sidebar.success(f"Welcome {st.session_state.user}")

    # ---------- ADD TRANSACTION ----------
    st.subheader("➕ Add Transaction")

    col1, col2, col3 = st.columns(3)

    with col1:
        t_type = st.selectbox("Type", ["Income","Expense"])
    with col2:
        category = st.selectbox("Category",
            ["Food","Rent","Travel","Shopping","Salary","Freelance","Other"])
    with col3:
        amount = st.number_input("Amount", min_value=0.0)

    if st.button("Add Transaction"):
        cur.execute("INSERT INTO transactions VALUES (NULL,?,?,?,?,?)",
                    (st.session_state.user, t_type, category, amount, str(datetime.now())))
        conn.commit()
        st.success("Transaction Added")

    # ---------- LOAD DATA ----------
    df = pd.read_sql_query(
        f"SELECT * FROM transactions WHERE user='{st.session_state.user}'",
        conn
    )

    if not df.empty:

        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M").astype(str)

        income = df[df["type"]=="Income"]["amount"].sum()
        expense = df[df["type"]=="Expense"]["amount"].sum()
        savings = income - expense

        # ---------- METRICS ----------
        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Income", income)
        col2.metric("💸 Expense", expense)
        col3.metric("💵 Savings", savings)

        # ---------- CHARTS ----------
        st.subheader("📊 Analytics")

        fig1 = px.pie(
            df, names="category", values="amount",
            color_discrete_sequence=px.colors.sequential.Tealgrn,
            template="plotly_dark"
        )
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(
            df, x="category", y="amount", color="type",
            color_discrete_sequence=px.colors.qualitative.Set2,
            template="plotly_dark"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # ---------- TREND ----------
        st.subheader("📈 Monthly Trend")

        trend = df.groupby(["month","type"])["amount"].sum().reset_index()
        fig3 = px.line(
            trend, x="month", y="amount", color="type",
            color_discrete_sequence=px.colors.qualitative.Bold,
            template="plotly_dark"
        )
        st.plotly_chart(fig3, use_container_width=True)

        # ---------- GOALS ----------
        st.subheader("🎯 Goal Tracking")

        goal_name = st.text_input("Goal (Car/House/etc)")
        target = st.number_input("Target Amount", min_value=0.0)

        if st.button("Set Goal"):
            cur.execute("INSERT INTO goals VALUES (NULL,?,?,?,?)",
                        (st.session_state.user, goal_name, target, savings))
            conn.commit()

        goals = pd.read_sql_query(
            f"SELECT * FROM goals WHERE user='{st.session_state.user}'",
            conn
        )

        if not goals.empty:
            for _, row in goals.iterrows():
                progress = row["saved"] / row["target"] if row["target"] > 0 else 0
                st.write(f"{row['goal_name']} Progress")
                st.progress(progress)

        # ---------- AI ----------
        st.subheader("🤖 AI Advisor")

        ratio = (expense / income)*100 if income > 0 else 0
        st.write(f"Expense Ratio: {round(ratio,2)}%")

        if ratio > 80:
            st.error("Reduce expenses urgently")
        elif ratio > 50:
            st.warning("Control spending")
        else:
            st.success("Good financial health")

        # ---------- FUTURE ----------
        future = savings * 12 * 10
        st.info(f"📊 10-Year Savings: ₹{future}")

        # ---------- EXPORT ----------
        st.subheader("📥 Export Data")
        csv = df.to_csv(index=False)
        st.download_button("Download Report", csv, "finance_report.csv")

    else:
        st.info("No transactions yet")
