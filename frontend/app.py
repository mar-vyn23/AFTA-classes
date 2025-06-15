import plotly.express as px
from io import StringIO
import streamlit as st
import pandas as pd
import requests
import os

API_URL = "https://school-loan-backend.onrender.com"
#API_URL = "http://127.0.0.1:8000"


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CSV_FILE = os.path.join(BASE_DIR, "../shared_data/savings.csv")

st.set_page_config(page_title="School Loan System")
st.title("🏫 School Loan Calculator")

menu = st.sidebar.radio("📂 Menu", ["Dashboard", "Register Savings Plan", "Check Loan Eligibility", "Download / Upload CSV"])

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=["user_id", "monthly_saving", "start_date"])

if menu == "Dashboard":
    st.subheader("📊 Dashboard Overview")
    df = load_data()

    if df.empty:
        st.warning("No savings data found.")
    else:
        total_users = df["user_id"].nunique()
        total_savings = df["monthly_saving"].sum()
        avg_saving = df["monthly_saving"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("👥 Total Users", total_users)
        col2.metric("💰 Total Monthly Savings", f"UGX {total_savings:,.0f}")
        col3.metric("📈 Average Saving", f"UGX {avg_saving:,.0f}")

        st.markdown("### 🧾 All Savings Records")
        st.dataframe(df)

        st.markdown("### 📉 Savings Distribution")
        fig = px.bar(df, x="user_id", y="monthly_saving", title="Monthly Savings by User", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)

if menu == "Register Savings Plan":
    st.subheader("📅 Enter Monthly Savings")
    user_id = st.text_input("User ID").strip().lower()
    monthly = st.number_input("Monthly Saving (UGX)", step=1000.0)

    if st.button("Save"):
            res = requests.post(f"{API_URL}/save", json={
                "user_id": user_id,
                "monthly_saving": monthly
            })
            if res.status_code == 200:
                st.success(res.json()["message"])
            else:
                st.error(res.json().get("detail", "Error saving data."))

elif menu == "Check Loan Eligibility":
    st.subheader("💳 Check Loan Eligibility")
    user_id = st.text_input("User ID").strip().lower()

    if st.button("Get Loan Info"):
        if user_id:
            try:
                res = requests.post(f"{API_URL}/loan", json={"user_id": user_id})
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Months Saved: {data['months_saved']}")
                    st.info(f"Total Saved: UGX {data['total_saved']:,.0f}")
                    st.success(f"Loan Eligible: UGX {data['loan_eligible_amount']:,.0f}")
                else:
                    try:
                        st.error(res.json().get("detail", "Error checking loan."))
                    except Exception:
                        st.error(f"Server error: {res.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Connection error: {e}")

elif menu == "Download / Upload CSV":
    st.subheader("📁 Current Savings Data")

    try:
        res = requests.get(f"{API_URL}/csv")
        if res.status_code == 200:
            df = pd.read_csv(StringIO(res.text))
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📤 Download CSV", data=res.content, file_name="savings.csv", mime='text/csv')
        else:
            st.warning("Unable to fetch CSV from backend.")
    except Exception as e:
        st.error(f"Error fetching CSV: {e}")

