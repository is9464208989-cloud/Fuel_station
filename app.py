import streamlit as st
import pandas as pd
from datetime import date

# --- 1. CONFIGURATION & STATE ---
if 'nozzles' not in st.session_state:
    st.session_state.nozzles = {"Petrol 1": "Petrol", "Diesel 1": "Diesel"}

if 'udhaar_data' not in st.session_state:
    st.session_state.udhaar_data = pd.DataFrame(columns=["Date", "Customer", "Amount", "Status"])

# New State for Cash/Online Accounting
if 'daily_cash' not in st.session_state:
    st.session_state.daily_cash = 0.0
if 'daily_online' not in st.session_state:
    st.session_state.daily_online = 0.0

if 'page' not in st.session_state:
    st.session_state.page = "Home"

if 'confirm_id' not in st.session_state:
    st.session_state.confirm_id = None

# --- 2. THEME & HEADER ---
st.set_page_config(page_title="petrol pump", layout="centered")
today = date.today()

# --- 3. PAGE NAVIGATION LOGIC ---

# --- HOME PAGE ---
if st.session_state.page == "Home":
    st.title("⛽ petrol pump")
    st.subheader(f"📅 {today.strftime('%d %B, %Y')}")
    
    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    if not pending_df.empty:
        st.warning(f"🔔 NOTIFICATION: {len(pending_df)} Pending entries!")
    else:
        st.success("✅ All Udhaar cleared!")

    # Dashboard Buttons
    if st.button("📊\n\nSTOCKS", use_container_width=True):
        st.session_state.page = "Stocks"
        st.rerun()
    if st.button("📒\n\nUDHAAR", use_container_width=True):
        st.session_state.page = "Udhaar"
        st.rerun()
    if st.button("💰\n\nCASH COLLECTED", use_container_width=True):
        st.session_state.page = "Cash_Collected"
        st.rerun()
    if st.button("⚙️\n\nSETTINGS", use_container_width=True):
        st.session_state.page = "Settings"
        st.rerun()

# --- CASH COLLECTED PAGE ---
elif st.session_state.page == "Cash_Collected":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    
    st.header("💰 Cash & Online Entry")
    with st.form("cash_form"):
        cash = st.number_input("Total Hard Cash Collected (₹)", value=None, placeholder="Enter cash amount...")
        online = st.number_input("Total Online/UPI Received (₹)", value=None, placeholder="Enter online amount...")
        if st.form_submit_button("SAVE COLLECTIONS", use_container_width=True):
            st.session_state.daily_cash = cash if cash else 0.0
            st.session_state.daily_online = online if online else 0.0
            st.success("Collections Saved!")
            st.session_state.page = "Home"
            st.rerun()

# --- STOCKS PAGE (WITH BEAUTIFUL SUMMARY) ---
elif st.session_state.page == "Stocks":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    
    st.header("🛢️ Daily Stock Entry")
    c1, c2 = st.columns(2)
    p_rate = c1.number_input("Petrol Rate (₹)", value=None, placeholder="Petrol Rate...", step=0.1)
    d_rate = c2.number_input("Diesel Rate (₹)", value=None, placeholder="Diesel Rate...", step=0.1)

    readings = []
    for name, fuel_type in st.session_state.nozzles.items():
        with st.container(border=True):
            st.write(f"**{name} ({fuel_type})**")
            op = st.number_input(f"Opening", key=f"{name}_op", value=None, placeholder="Opening...")
            cl = st.number_input(f"Closing", key=f"{name}_cl", value=None, placeholder="Closing...")
            
            rate = (p_rate if p_rate else 0) if fuel_type == "Petrol" else (d_rate if d_rate else 0)
            sale = (cl if cl else 0) - (op if op else 0)
            readings.append({"Nozzle": name, "Sale": sale, "Amount": sale * rate})

    if st.button("VIEW FINAL SUMMARY", type="primary", use_container_width=True):
        st.divider()
        st.subheader("📊 Final Shift Summary")
        
        required_amt = sum(item['Amount'] for item in readings)
        collected_amt = st.session_state.daily_cash + st.session_state.daily_online
        difference = collected_amt - required_amt
        
        # Beautiful Metric Display
        m1, m2 = st.columns(2)
        m1.metric("Required (Machine)", f"₹{required_amt:,.2f}")
        m2.metric("Collected (Actual)", f"₹{collected_amt:,.2f}")
        
        if difference < 0:
            st.error(f"⚠️ SHORTAGE: ₹{abs(difference):,.2f}")
        elif difference > 0:
            st.success(f"✅ EXCESS: ₹{difference:,.2f}")
        else:
            st.info("🎯 PERFECT MATCH: No difference!")
            
        st.table(pd.DataFrame(readings))

# --- UDHAAR LOGIC (STAYS THE SAME) ---
elif st.session_state.page == "Udhaar":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    
    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    total_left = pending_df["Amount"].sum()
    st.metric(label="Total Udhaar Left", value=f"₹{total_left:,.2f}")
    
    if st.button("➕ ADD NEW UDHAAR", use_container_width=True):
        st.session_state.page = "Add_Udhaar"
        st.rerun()
    if st.button("✅ CLEAR PENDING UDHAAR", use_container_width=True):
        st.session_state.page = "Clear_List"
        st.rerun()

# --- (Rest of the pages: Add_Udhaar, Clear_List, Confirm_Clear, Settings stay exactly as before) ---
elif st.session_state.page == "Add_Udhaar":
    if st.button("⬅ BACK TO UDHAAR MENU", use_container_width=True):
        st.session_state.page = "Udhaar"
        st.rerun()
    st.header("➕ New Entry")
    with st.form("new_u", clear_on_submit=True):
        u_cust = st.text_input("Customer Name (Required)")
        u_amt = st.number_input("Amount (₹)", value=None, placeholder="Enter Amount...")
        u_date = st.date_input("Select Date", today)
        if st.form_submit_button("SAVE", use_container_width=True):
            if u_cust.strip() and u_amt and u_amt > 0:
                new_row = pd.DataFrame([{"Date": str(u_date), "Customer": u_cust, "Amount": u_amt, "Status": "Pending 🔴"}])
                st.session_state.udhaar_data = pd.concat([st.session_state.udhaar_data, new_row], ignore_index=True)
                st.success(f"SAVED: {u_cust}")
                st.session_state.page = "Home"
                st.rerun()
            else:
                st.error("Invalid Entry")

elif st.session_state.page == "Clear_List":
    if st.button("⬅ BACK TO UDHAAR MENU", use_container_width=True):
        st.session_state.page = "Udhaar"
        st.rerun()
    st.header("📋 Pending List")
    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    for index, row in pending_df.iterrows():
        if st.button(f"{row['Customer']} - ₹{row['Amount']} ({row['Date']})", key=f"list_{index}", use_container_width=True):
            st.session_state.confirm_id = index
            st.session_state.page = "Confirm_Clear"
            st.rerun()

elif st.session_state.page == "Confirm_Clear":
    idx = st.session_state.confirm_id
    row = st.session_state.udhaar_data.loc[idx]
    st.warning("⚠️ FINAL CONFIRMATION")
    st.write(f"Clear Udhaar for **{row['Customer']}**?")
    if st.button("YES, MARK AS PAID 🟢", use_container_width=True):
        st.session_state.udhaar_data.at[idx, "Status"] = "Cleared ✅"
        st.balloons()
        st.session_state.page = "Home"
        st.rerun()
    if st.button("CANCEL", use_container_width=True):
        st.session_state.page = "Clear_List"
        st.rerun()

elif st.session_state.page == "Settings":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    st.header("⚙️ Configuration")
    with st.container(border=True):
        st.subheader("Add Nozzle")
        new_name = st.text_input("Nozzle Name")
        new_type = st.selectbox("Type", ["Petrol", "Diesel"])
        if st.button("SAVE NOZZLE", use_container_width=True):
            if new_name:
                st.session_state.nozzles[new_name] = new_type
                st.rerun()
    with st.container(border=True):
        st.subheader("Delete Nozzle")
        if st.session_state.nozzles:
            to_del = st.selectbox("Select to Remove", list(st.session_state.nozzles.keys()))
            if st.button("DELETE PERMANENTLY", type="primary", use_container_width=True):
                del st.session_state.nozzles[to_del]
                st.rerun()
