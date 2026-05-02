import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# DB
conn = sqlite3.connect("finance.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
age INTEGER,
category TEXT,
income REAL)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS transactions (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
type TEXT,
category TEXT,
amount REAL)
""")

conn.commit()

st.title("💰 Finance Analytics System")

# USER INPUT
name = st.sidebar.text_input("Name")
age = st.sidebar.number_input("Age", 10, 100)
category = st.sidebar.selectbox("Category", ["student","professional","business"])
income = st.sidebar.number_input("Monthly Income")

if st.sidebar.button("Login"):
    cur.execute("INSERT INTO users(name, age, category, income) VALUES (?,?,?,?)",
                (name, age, category, income))
    conn.commit()
    st.session_state.user_id = cur.lastrowid

if "user_id" in st.session_state:

    st.header("Add Transaction")

    t_type = st.selectbox("Type", ["Income","Expense"])
    cat = st.text_input("Category")
    amt = st.number_input("Amount")

    if st.button("Add"):
        cur.execute("INSERT INTO transactions(user_id,type,category,amount) VALUES (?,?,?,?)",
                    (st.session_state.user_id, t_type, cat, amt))
        conn.commit()

    df = pd.read_sql_query(f"SELECT * FROM transactions WHERE user_id={st.session_state.user_id}", conn)

    if not df.empty:
        income_total = df[df["type"]=="Income"]["amount"].sum()
        expense_total = df[df["type"]=="Expense"]["amount"].sum()

        st.write("Income:", income_total)
        st.write("Expense:", expense_total)

        fig = px.pie(df, names="category", values="amount")
        st.plotly_chart(fig)