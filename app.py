import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
</style>
""", unsafe_allow_html=True)

# ---------- DATABASE ----------
conn = sqlite3.connect("finance.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")
conn.commit()

# ---------- HEADER ----------
st.title("💰 Finance Analytics & Management System")
st.write("👉 Enter your financial details and get a complete, easy-to-understand analysis.")

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
            st.success("Account created successfully")
        except:
            st.error("Username already exists")

elif choice == "Login":
    st.subheader("Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        res = cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (user,pwd)
        ).fetchone()

        if res:
            st.session_state.logged = True
            st.session_state.user = user
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

# ---------- MAIN ----------
if "logged" in st.session_state:

    st.sidebar.success(f"Welcome {st.session_state.user}")

    # STEP 1
    st.header("Step 1: Enter Monthly Income")
    st.write("👉 Enter the total money you earn in one month")

    income = st.number_input("Monthly Income (₹)", min_value=0.0)

    # STEP 2 (VERTICAL CLEAR)
    st.header("Step 2: Enter Monthly Expenses")
    st.write("👉 Enter how much you spend in each category")

    expenses = {}
    total_expense = 0

    food = st.number_input("Enter how much you spend on Food (₹)", min_value=0.0)
    expenses["Food"] = food
    total_expense += food

    rent = st.number_input("Enter how much you spend on Rent (₹)", min_value=0.0)
    expenses["Rent"] = rent
    total_expense += rent

    travel = st.number_input("Enter how much you spend on Travel (₹)", min_value=0.0)
    expenses["Travel"] = travel
    total_expense += travel

    shopping = st.number_input("Enter how much you spend on Shopping (₹)", min_value=0.0)
    expenses["Shopping"] = shopping
    total_expense += shopping

    bills = st.number_input("Enter how much you spend on Bills (₹)", min_value=0.0)
    expenses["Bills"] = bills
    total_expense += bills

    entertainment = st.number_input("Enter how much you spend on Entertainment (₹)", min_value=0.0)
    expenses["Entertainment"] = entertainment
    total_expense += entertainment

    healthcare = st.number_input("Enter how much you spend on Healthcare (₹)", min_value=0.0)
    expenses["Healthcare"] = healthcare
    total_expense += healthcare

    education = st.number_input("Enter how much you spend on Education (₹)", min_value=0.0)
    expenses["Education"] = education
    total_expense += education

    other = st.number_input("Enter how much you spend on Other (₹)", min_value=0.0)
    expenses["Other"] = other
    total_expense += other

    savings = income - total_expense
    ratio = (total_expense / income * 100) if income > 0 else 0

    # STEP 3
    st.header("Step 3: Financial Summary")

    c1,c2,c3 = st.columns(3)
    c1.metric("Income", income)
    c2.metric("Expense", total_expense)
    c3.metric("Savings", savings)

    st.write(f"👉 Expense Ratio: {round(ratio,2)}%")

    st.markdown("""
- 🟢 Below 50% → Good  
- 🟡 50–80% → Moderate  
- 🔴 Above 80% → Overspending  
""")

    # STEP 4
    st.header("Step 4: Expense Distribution")

    df = pd.DataFrame({
        "Category": list(expenses.keys()),
        "Amount": list(expenses.values())
    })

    df = df[df["Amount"] > 0]

    if not df.empty:
        fig = px.pie(df, names="Category", values="Amount", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    # STEP 5
    st.header("Step 5: Future Savings")

    years = st.slider("Select years", 1, 10, 5)
    future = savings * 12 * years

    st.info(f"👉 After {years} years, you may save ₹{round(future,2)}")

    # STEP 6
    st.header("Step 6: Goal Planning")

    st.write("👉 Enter your goal amount and years to achieve it")

    goal = st.number_input("Target Amount (₹)", min_value=0.0)
    goal_years = st.selectbox("Years", [3,5,10])

    if goal > 0:
        required = goal / (goal_years * 12)

        st.write(f"👉 You must save ₹{round(required,2)} per month")

        if savings >= required:
            st.success("🟢 On track")
        else:
            st.warning("🟡 Increase savings")

    # STEP 7
    st.header("Step 7: AI Advice")

    if ratio > 80:
        st.error("🔴 You are overspending")
    elif ratio > 50:
        st.warning("🟡 Control expenses")
    else:
        st.success("🟢 Good spending")

    if savings <= 0:
        st.error("🔴 No savings")
    elif savings < income*0.2:
        st.warning("🟡 Increase savings")
    else:
        st.success("🟢 Strong savings")

    # STEP 8
    st.header("Step 8: Income Growth Simulation")

    options = [
        "Freelancing","Stock Market","Mutual Funds","Real Estate",
        "YouTube","E-commerce","Startup","Consulting",
        "Affiliate Marketing","Teaching"
    ]

    choice = st.selectbox("Select method", options)
    g_years = st.slider("Years for growth",1,10,5)

    mult = {
        "Freelancing":1.5,"Stock Market":2,"Mutual Funds":1.8,
        "Real Estate":2.2,"YouTube":2.5,"E-commerce":2.8,
        "Startup":3,"Consulting":2.3,"Affiliate Marketing":2,"Teaching":2.2
    }

    future_income = income * mult[choice]
    total_future = future_income * 12 * g_years

    st.info(f"👉 Estimated income after {g_years} years: ₹{round(total_future,2)}")

    # STEP 9
    st.header("Step 9: Financial Score")

    score = 0

    if income > 0:
        sr = savings/income
        if sr >= 0.3: score += 40
        elif sr >= 0.2: score += 30
        elif sr >= 0.1: score += 20
        else: score += 10

    if ratio < 50: score += 40
    elif ratio < 80: score += 25
    else: score += 10

    if goal > 0:
        if savings >= required: score += 20
        else: score += 5

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Financial Score"},
        gauge={'axis': {'range': [0,100]}}
    ))

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
- 🟢 80–100 → Excellent  
- 🟡 50–79 → Average  
- 🔴 Below 50 → Needs Improvement  
""")

    # STEP 10
    st.header("Step 10: Final Result")

    if score >= 80:
        st.success("🟢 GOLD – Excellent")
    elif score >= 50:
        st.warning("🟡 SILVER – Average")
    else:
        st.error("🔴 BRONZE – Needs Improvement")

    # STEP 11
    st.header("Download Report")

    report = pd.DataFrame({
        "Income":[income],
        "Expense":[total_expense],
        "Savings":[savings],
        "Score":[score]
    })

    st.download_button("Download CSV", report.to_csv(index=False), "finance_report.csv")

else:
    st.info("Login to continue")
