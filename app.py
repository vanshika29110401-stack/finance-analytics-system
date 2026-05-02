import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# ---------- CONFIG ----------
st.set_page_config(page_title="Finance System", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: white; }
h1,h2,h3 { color: #00c6ff; }

.stButton>button {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color: white;
    border-radius: 8px;
}

[data-testid="metric-container"] {
    background: #1c1f26;
    padding: 15px;
    border-radius: 10px;
}
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

conn.commit()

# ---------- HEADER ----------
st.title("💰 Finance Analytics & Management System")

# ---------- AUTH ----------
menu = ["Register","Login"]
choice = st.sidebar.radio("Menu", menu)

if choice == "Register":
    st.subheader("Create Account")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Register"):
        try:
            cur.execute("INSERT INTO users(username,password) VALUES (?,?)",(user,pwd))
            conn.commit()
            st.success("Account Created! Go to Login")
        except:
            st.error("Username already exists")

elif choice == "Login":
    st.subheader("Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        result = cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user,pwd)
        ).fetchone()

        if result:
            st.session_state.logged = True
            st.session_state.user = user
            st.success("Login Successful")
        else:
            st.error("Invalid Credentials")

# ---------- MAIN APP ----------
if "logged" in st.session_state:

    st.sidebar.success(f"Welcome {st.session_state.user}")

    # ---------- INPUT ----------
    st.header("💰 Monthly Financial Input")

    income = st.number_input("Enter Monthly Income (₹)", min_value=0.0)

    st.subheader("💸 Expenses (Category-wise)")

    categories = ["Food","Rent","Travel","Shopping","Bills","Other"]

    expenses = {}
    total_expense = 0

    for cat in categories:
        val = st.number_input(f"{cat}", min_value=0.0, key=cat)
        expenses[cat] = val
        total_expense += val

    savings = income - total_expense

    # ---------- SUMMARY ----------
    st.header("📊 Financial Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Income", income)
    col2.metric("Expense", total_expense)
    col3.metric("Savings", savings)

    ratio = (total_expense / income * 100) if income > 0 else 0
    st.write(f"Expense Ratio: {round(ratio,2)}%")

    # ---------- CHART ----------
    expense_df = pd.DataFrame({
        "Category": list(expenses.keys()),
        "Amount": list(expenses.values())
    })

    expense_df = expense_df[expense_df["Amount"] > 0]

    if not expense_df.empty:
        fig = px.pie(expense_df, names="Category", values="Amount",
                     template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # ---------- FUTURE ----------
    st.header("📈 Future Projection")

    years = st.slider("Select Years", 1, 10, 5)

    future = savings * 12 * years
    st.info(f"Estimated savings after {years} years: ₹{future}")

    # ---------- GOAL ----------
    st.header("🎯 Goal Planning")

    goal = st.number_input("Enter Target Amount (₹)", min_value=0.0)
    goal_years = st.selectbox("Time Period", [5,10])

    if goal > 0:
        required = goal / (goal_years * 12)

        st.write(f"Required monthly saving: ₹{round(required,2)}")

        if savings >= required:
            st.success("You are on track!")
        else:
            st.warning("Increase savings to reach goal")

    # ---------- AI SUGGESTION ----------
    st.header("🤖 AI Financial Advisor")

    if ratio > 80:
        st.error("You are overspending. Reduce expenses.")
    elif ratio > 50:
        st.warning("Try to control spending.")
    else:
        st.success("Good financial discipline!")

    if savings <= 0:
        st.error("No savings. Reduce expenses.")
    elif savings < income * 0.2:
        st.warning("Increase savings to at least 20%.")
    else:
        st.success("Excellent savings habit!")

    # ---------- GROWTH ----------
    st.header("📊 Income Growth Simulation")

    option = st.selectbox("Choose Strategy",
                          ["Freelancing","Investing","Business"])

    if option == "Freelancing":
        future_income = income + 20000
    elif option == "Investing":
        future_income = income * 1.8
    else:
        future_income = income * 2.5

    total_future = future_income * 12 * 10

    st.info(f"Estimated income after 10 years: ₹{round(total_future,2)}")

    # ---------- EXPORT ----------
    st.header("📥 Download Report")

    report = pd.DataFrame({
        "Income":[income],
        "Expense":[total_expense],
        "Savings":[savings],
        "Expense Ratio":[ratio]
    })

    csv = report.to_csv(index=False)

    st.download_button("Download Report", csv, "finance_report.csv")

else:
    st.info("Please Login to Continue")
