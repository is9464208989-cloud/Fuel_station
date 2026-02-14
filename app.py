import streamlit as st
import pandas as pd
from datetime import date

# --- 1. CONFIGURATION & STATE ---
if 'nozzles' not in st.session_state:
    st.session_state.nozzles = {"Petrol 1": "Petrol", "Diesel 1": "Diesel"}

if 'udhaar_data' not in st.session_state:
    st.session_state.udhaar_data = pd.DataFrame(columns=["Date", "Customer", "Amount", "Status"])

if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Track which specific Udhaar we are confirming
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

    if st.button("📊\n\nSTOCKS", use_container_width=True):
        st.session_state.page = "Stocks"
        st.rerun()
    if st.button("📒\n\nUDHAAR", use_container_width=True):
        st.session_state.page = "Udhaar"
        st.rerun()
    if st.button("⚙️\n\nSETTINGS", use_container_width=True):
        st.session_state.page = "Settings"
        st.rerun()

# --- STOCKS PAGE ---
elif st.session_state.page == "Stocks":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    st.header("🛢️ Daily Stock Entry")
    # ... (Stocks logic remains same)

# --- UDHAAR MAIN PAGE ---
elif st.session_state.page == "Udhaar":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    
    # CALCULATE TOTAL UDHAAR
    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    total_left = pending_df["Amount"].sum()
    
    st.metric(label="Total Udhaar Left", value=f"₹{total_left:,.2f}")
    
    if st.button("➕ ADD NEW UDHAAR", use_container_width=True):
        st.session_state.page = "Add_Udhaar"
        st.rerun()
    if st.button("✅ CLEAR PENDING UDHAAR", use_container_width=True):
        st.session_state.page = "Clear_List"
        st.rerun()

# --- ADD NEW UDHAAR PAGE ---
elif st.session_state.page == "Add_Udhaar":
    if st.button("⬅ BACK TO UDHAAR MENU", use_container_width=True):
        st.session_state.page = "Udhaar"
        st.rerun()
    
    st.header("➕ New Entry")
    with st.form("new_u"):
        u_cust = st.text_input("Customer Name (Required)")
        u_amt = st.number_input("Amount (₹)", min_value=0.0)
        if st.form_submit_button("SAVE", use_container_width=True):
            if u_cust.strip() and u_amt > 0:
                new_row = pd.DataFrame([{"Date": str(today), "Customer": u_cust, "Amount": u_amt, "Status": "Pending 🔴"}])
                st.session_state.udhaar_data = pd.concat([st.session_state.udhaar_data, new_row], ignore_index=True)
                st.success("SAVED!")
                st.session_state.page = "Udhaar"
                st.rerun()
            else:
                st.error("Invalid Name/Amount")

# --- CLEAR PENDING LIST PAGE ---
elif st.session_state.page == "Clear_List":
    if st.button("⬅ BACK TO UDHAAR MENU", use_container_width=True):
        st.session_state.page = "Udhaar"
        st.rerun()
    
    st.header("📋 Pending List")
    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    
    for index, row in pending_df.iterrows():
        if st.button(f"{row['Customer']} - ₹{row['Amount']}", key=f"list_{index}", use_container_width=True):
            st.session_state.confirm_id = index
            st.session_state.page = "Confirm_Clear"
            st.rerun()

# --- FINAL CONFIRMATION PAGE ---
elif st.session_state.page == "Confirm_Clear":
    idx = st.session_state.confirm_id
    row = st.session_state.udhaar_data.loc[idx]
    
    st.warning("⚠️ FINAL CONFIRMATION")
    st.write(f"Are you sure you want to clear Udhaar for **{row['Customer']}**?")
    st.write(f"**Amount:** ₹{row['Amount']}")
    
    if st.button("YES, MARK AS PAID 🟢", use_container_width=True):
        st.session_state.udhaar_data.at[idx, "Status"] = "Cleared ✅"
        st.balloons()
        st.session_state.page = "Udhaar"
        st.rerun()
    
    if st.button("CANCEL", use_container_width=True):
        st.session_state.page = "Clear_List"
        st.rerun()

# --- SETTINGS PAGE ---
elif st.session_state.page == "Settings":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
    # ... (Settings logic remains same)
