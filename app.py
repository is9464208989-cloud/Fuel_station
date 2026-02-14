import streamlit as st
import pandas as pd
from datetime import date

# --- 1. CONFIGURATION & STATE ---
if 'nozzles' not in st.session_state:
    st.session_state.nozzles = {
        "Petrol 1": "Petrol", "Petrol 2": "Petrol",
        "Diesel 1": "Diesel", "Diesel 2": "Diesel"
    }

if 'udhaar_data' not in st.session_state:
    st.session_state.udhaar_data = pd.DataFrame(columns=["Date", "Customer", "Amount", "Status"])

if 'page' not in st.session_state:
    st.session_state.page = "Home"

# --- 2. THEME & HEADER ---
st.set_page_config(page_title="petrol pump", layout="centered")
today = date.today()

# --- 3. PAGE NAVIGATION LOGIC ---

# --- HOME PAGE ---
if st.session_state.page == "Home":
    st.title("⛽ petrol pump")
    st.subheader(f"📅 {today.strftime('%d %B, %Y')}")

    # Notifications
    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    if not pending_df.empty:
        st.warning(f"🔔 NOTIFICATION: {len(pending_df)} Pending Udhaar entries!")
    else:
        st.success("✅ All Udhaar cleared!")

    st.write("### Main Menu")
    # Big Interactive Blocks
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
    c1, c2 = st.columns(2)
    p_rate = c1.number_input("Petrol Rate (₹)", value=95.0, step=0.1)
    d_rate = c2.number_input("Diesel Rate (₹)", value=88.0, step=0.1)

    readings = []
    for name, fuel_type in st.session_state.nozzles.items():
        with st.container(border=True):
            st.write(f"**{name} ({fuel_type})**")
            op = st.number_input(f"Opening", key=f"{name}_op", min_value=0.0)
            cl = st.number_input(f"Closing", key=f"{name}_cl", min_value=0.0)
            current_rate = p_rate if fuel_type == "Petrol" else d_rate
            sale = cl - op
            amt = sale * current_rate
            readings.append({"Nozzle": name, "Sale (Ltr)": sale, "Amount (₹)": amt})

    if st.button("CALCULATE SUMMARY", type="primary", use_container_width=True):
        total_cash = sum(item['Amount (₹)'] for item in readings)
        st.success(f"### Total Cash: ₹{total_cash:,.2f}")
        st.table(pd.DataFrame(readings))

# --- UDHAAR PAGE ---
elif st.session_state.page == "Udhaar":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"
        st.rerun()
        
    tab1, tab2 = st.tabs(["➕ Add New", "✅ Clear Pending"])
    
    with tab1:
        with st.form("new_udhaar", clear_on_submit=True):
            u_cust = st.text_input("Customer/Vehicle Name (Required)")
            u_amt = st.number_input("Amount (₹) (Required)", min_value=0.0)
            u_date = st.date_input("Date", today)
            
            if st.form_submit_button("SAVE", use_container_width=True):
                if not u_cust.strip() or u_amt <= 0:
                    st.error("❌ INVALID: Name and Amount (>0) are required!")
                else:
                    new_row = pd.DataFrame([{"Date": str(u_date), "Customer": u_cust, "Amount": u_amt, "Status": "Pending 🔴"}])
                    st.session_state.udhaar_data = pd.concat([st.session_state.udhaar_data, new_row], ignore_index=True)
                    st.success(f"✅ SAVED: {u_cust}")
                    st.balloons()
                    # This sends you back to the home page notification after saving
                    st.session_state.page = "Home"
                    st.rerun()

    with tab2:
        pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
        if pending_df.empty:
            st.info("No pending Udhaar.")
        else:
            for index, row in pending_df.iterrows():
                with st.container(border=True):
                    st.write(f"**{row['Customer']}** | ₹{row['Amount']}")
                    if st.button("Mark Paid 🟢", key=f"clr_{index}", use_container_width=True):
                        st.session_state.udhaar_data.at[index, "Status"] = "Cleared ✅"
                        st.rerun()

# --- SETTINGS PAGE ---
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
