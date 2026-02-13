import streamlit as st
import pandas as pd
from datetime import date

# --- 1. CONFIGURATION & STATE ---
# This part saves your nozzle names and allows you to add more later
if 'nozzles' not in st.session_state:
    st.session_state.nozzles = {
        "Petrol 1": "Petrol", "Petrol 2": "Petrol",
        "Diesel 1": "Diesel", "Diesel 2": "Diesel"
    }

# Mock database for Udhaar (In a real app, this connects to a CSV or Google Sheet)
if 'udhaar_data' not in st.session_state:
    st.session_state.udhaar_data = [
        {"Date": "2026-02-12", "Customer": "PB-07-Truck", "Amount": 5000, "Status": "Pending 🔴"},
    ]

# --- 2. TOP BAR (Automatic Date) ---
st.set_page_config(page_title="Railmajra Pump Pro")
st.title(f"⛽ Railmajra Pump")
st.subheader(f"📅 Date: {date.today().strftime('%d %B, %Y')}")

# Check for pending Udhaar from previous dates
pending_count = len([x for x in st.session_state.udhaar_data if "Pending" in x["Status"]])
if pending_count > 0:
    st.warning(f"🔔 Notification: There are {pending_count} pending Udhaar entries from previous days!")

# --- 3. MAIN NAVIGATION ---
option = st.radio("Select Action:", ["Stocks (Nozzle Readings)", "Udhaar Ledger", "Settings (Add Nozzles)"], horizontal=True)

# --- 4. STOCKS PAGE ---
if option == "Stocks (Nozzle Readings)":
    st.header("🛢️ Daily Stock Entry")
    
    col1, col2 = st.columns(2)
    with col1:
        p_rate = st.number_input("Current Petrol Rate (₹)", value=95.0, step=0.1)
    with col2:
        d_rate = st.number_input("Current Diesel Rate (₹)", value=88.0, step=0.1)

    readings = []
    for name, fuel_type in st.session_state.nozzles.items():
        with st.expander(f"Reading for {name} ({fuel_type})"):
            op = st.number_input(f"{name} Opening", key=f"{name}_op", min_value=0.0)
            cl = st.number_input(f"{name} Closing", key=f"{name}_cl", min_value=0.0)
            current_rate = p_rate if fuel_type == "Petrol" else d_rate
            
            sale = cl - op
            amt = sale * current_rate
            readings.append({"Nozzle": name, "Sale": sale, "Amount": amt})

    if st.button("Calculate Final Summary"):
        total_cash = sum(item['Amount'] for item in readings)
        st.success(f"### Total Cash to Collect Today: ₹{total_cash:,.2f}")
        st.table(pd.DataFrame(readings))

# --- 5. UDHAAR PAGE ---
elif option == "Udhaar Ledger":
    st.header("📒 Udhaar Management")
    
    # New Entry Form
    with st.form("new_udhaar"):
        st.write("Add New Udhaar")
        u_cust = st.text_input("Customer Name / Vehicle No.")
        u_amt = st.number_input("Amount (₹)", min_value=0.0)
        u_date = st.date_input("Udhaar Date", date.today())
        if st.form_submit_button("Save Entry"):
            st.session_state.udhaar_data.append({"Date": str(u_date), "Customer": u_cust, "Amount": u_amt, "Status": "Pending 🔴"})
            st.rerun()

    # Summary List
    st.write("### Pending & Recent Udhaar Summary")
    df_udhaar = pd.DataFrame(st.session_state.udhaar_data)
    if not df_udhaar.empty:
        st.dataframe(df_udhaar.sort_values("Date", ascending=False), use_container_width=True)

# --- 6. SETTINGS (Add New Nozzles) ---
elif option == "Settings (Add Nozzles)":
    st.header("⚙️ Pump Configuration")
    new_name = st.text_input("New Nozzle Name (e.g., Diesel 3)")
    new_type = st.selectbox("Fuel Type", ["Petrol", "Diesel"])
    if st.button("Add Nozzle"):
        st.session_state.nozzles[new_name] = new_type
        st.success(f"Added {new_name} to the system!")
