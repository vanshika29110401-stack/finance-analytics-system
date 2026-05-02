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
    st.write("👉 Enter the total money you earn in one month (salary, pocket money, etc.)")

    income = st.number_input("Monthly Income (₹)", min_value=0.0)

    # STEP 2
    st.header("Step 2: Enter Monthly Expenses")
    st.write("👉 Enter how much you spend in each category below")

    expenses = {}
    total_expense = 0

    categories = [
        "Food Expense (₹)",
        "Rent Expense (₹)",
        "Travel Expense (₹)",
        "Shopping Expense (₹)",
        "Bills Expense (₹)",
        "Entertainment Expense (₹)",
        "Healthcare Expense (₹)",
        "Education Expense (₹)",
        "Other Expense (₹)"
    ]

    cols = st.columns(3)

    for i, cat in enumerate(categories):
        with cols[i % 3]:
            val = st.number_input(cat, min_value=0.0, key=cat)
            expenses[cat] = val
            total_expense += val

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
Meaning:
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

    st.write("👉 See how much you can save if you continue this spending pattern")

    years = st.slider("Select number of years", 1, 10, 5)
    future = savings * 12 * years

    st.info(f"👉 After {years} years, your estimated savings will be ₹{round(future,2)}")

    # STEP 6 (IMPROVED CLEAR INSTRUCTION)
    st.header("Step 6: Goal Planning")

    st.write("""
👉 Enter your financial goal:

- Example: Buying a car, house, or saving ₹5,00,000  
- Enter the **total amount you want to achieve**  
- Then select **in how many years** you want to achieve it  
""")

    goal = st.number_input("Enter your Target Amount (₹)", min_value=0.0)
    goal_years = st.selectbox("Select number of years to achieve goal", [3,5,10])

    if goal > 0:
        required = goal / (goal_years * 12)

        st.write(f"👉 To reach this goal, you must save ₹{round(required,2)} per month")

        if savings >= required:
            st.success("🟢 You are on track to achieve your goal")
        else:
            st.warning("🟡 You need to increase your monthly savings")

    # STEP 7
    st.header("Step 7: AI Financial Advice")

    if ratio > 80:
        st.error("🔴 You are overspending. Try reducing unnecessary expenses.")
    elif ratio > 50:
        st.warning("🟡 You should control your expenses.")
    else:
        st.success("🟢 Your spending is well managed.")

    if savings <= 0:
        st.error("🔴 You are not saving money.")
    elif savings < income * 0.2:
        st.warning("🟡 Try to save at least 20% of your income.")
    else:
        st.success("🟢 You have a strong saving habit.")

    # STEP 8
    st.header("Step 8: Income Growth Simulation")

    st.write("👉 Choose a practical way to increase your income in the future")

    options = [
        "Freelancing",
        "Stock Market Investing",
        "Mutual Funds (SIP)",
        "Real Estate",
        "YouTube / Content Creation",
        "Online Business / E-commerce",
        "Startup / Tech Business",
        "Consulting / Coaching",
        "Affiliate Marketing",
        "Online Teaching / Courses"
    ]

    choice = st.selectbox("Select income growth method", options)
    g_years = st.slider("Select years for growth", 1, 10, 5)

    multipliers = {
        "Freelancing":1.5,
        "Stock Market Investing":2,
        "Mutual Funds (SIP)":1.8,
        "Real Estate":2.2,
        "YouTube / Content Creation":2.5,
        "Online Business / E-commerce":2.8,
        "Startup / Tech Business":3,
        "Consulting / Coaching":2.3,
        "Affiliate Marketing":2,
        "Online Teaching / Courses":2.2
    }

    future_income = income * multipliers[choice]
    total_future = future_income * 12 * g_years

    st.info(f"👉 Estimated total income after {g_years} years: ₹{round(total_future,2)}")

    # STEP 9
    st.header("Step 9: Financial Score")

    score = 0

    if income > 0:
        sr = savings / income
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
        gauge={
            'axis': {'range': [0,100]},
            'steps': [
                {'range':[0,50],'color':'red'},
                {'range':[50,80],'color':'yellow'},
                {'range':[80,100],'color':'green'}
            ]
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
Score Meaning:
- 🟢 80–100 → Excellent  
- 🟡 50–79 → Average  
- 🔴 Below 50 → Needs Improvement  
""")

    # STEP 10
    st.header("Step 10: Final Financial Status")

    if score >= 80:
        st.success("🟢 GOLD – Excellent Financial Health")
    elif score >= 50:
        st.warning("🟡 SILVER – Stable Condition")
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
