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

# --- 2. TOP BAR & NOTIFICATIONS ---
st.set_page_config(page_title="Railmajra Pump Pro", layout="centered")
st.title(f"⛽ Railmajra Pump")
today = date.today()
st.subheader(f"📅 {today.strftime('%d %B, %Y')}")

pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
if not pending_df.empty:
    st.warning(f"🔔 NOTIFICATION: {len(pending_df)} Pending Udhaar entries!")
else:
    st.success("✅ All Udhaar cleared!")

# --- 3. BIG INTERACTIVE BLOCKS (Navigation) ---
st.write("### Main Menu")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊\n\nSTOCKS", use_container_width=True):
        st.session_state.page = "Stocks"
with col2:
    if st.button("📒\n\nUDHAAR", use_container_width=True):
        st.session_state.page = "Udhaar"
with col3:
    if st.button("⚙️\n\nSETTINGS", use_container_width=True):
        st.session_state.page = "Settings"

st.divider()

# --- 4. STOCKS (NOZZLE READINGS) ---
if st.session_state.page == "Stocks":
    st.header("🛢️ Daily Stock Entry")
    c1, c2 = st.columns(2)
    p_rate = c1.number_input("Petrol Rate (₹)", value=95.0, step=0.1)
    d_rate = c2.number_input("Diesel Rate (₹)", value=88.0, step=0.1)

    readings = []
    for name, fuel_type in st.session_state.nozzles.items():
        with st.expander(f"Readings for {name} ({fuel_type})", expanded=True):
            op = st.number_input(f"{name} Opening", key=f"{name}_op", min_value=0.0)
            cl = st.number_input(f"{name} Closing", key=f"{name}_cl", min_value=0.0)
            current_rate = p_rate if fuel_type == "Petrol" else d_rate
            sale = cl - op
            amt = sale * current_rate
            readings.append({"Nozzle": name, "Sale (Ltr)": sale, "Amount (₹)": amt})

    if st.button("Calculate Final Summary", type="primary", use_container_width=True):
        total_cash = sum(item['Amount (₹)'] for item in readings)
        st.success(f"### Total Cash to Collect: ₹{total_cash:,.2f}")
        st.table(pd.DataFrame(readings))

# --- 5. UDHAAR LEDGER (INTERACTIVE) ---
elif st.session_state.page == "Udhaar":
    tab1, tab2 = st.tabs(["➕ Add New Udhaar", "✅ Clear Pending"])
    
    with tab1:
        with st.form("new_udhaar"):
            u_cust = st.text_input("Customer/Vehicle Name")
            u_amt = st.number_input("Amount (₹)", min_value=0.0)
            u_date = st.date_input("Date", today)
            if st.form_submit_button("SAVE UDHAAR", use_container_width=True):
                new_row = pd.DataFrame([{"Date": str(u_date), "Customer": u_cust, "Amount": u_amt, "Status": "Pending 🔴"}])
                st.session_state.udhaar_data = pd.concat([st.session_state.udhaar_data, new_row], ignore_index=True)
                st.rerun()

    with tab2:
        if pending_df.empty:
            st.info("No pending Udhaar to clear.")
        else:
            for index, row in pending_df.iterrows():
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])
                    c1.write(f"**{row['Customer']}**\n₹{row['Amount']} | {row['Date']}")
                    if c2.button("Mark Paid 🟢", key=f"clr_{index}", use_container_width=True):
                        st.session_state.udhaar_data.at[index, "Status"] = "Cleared ✅"
                        st.balloons()
                        st.rerun()

# --- 6. SETTINGS ---
elif st.session_state.page == "Settings":
    st.header("⚙️ Configuration")
    with st.expander("Add New Nozzle"):
        new_name = st.text_input("Nozzle Name")
        new_type = st.selectbox("Type", ["Petrol", "Diesel"])
        if st.button("Save Nozzle", use_container_width=True):
            st.session_state.nozzles[new_name] = new_type
            st.rerun()

    with st.expander("Delete Nozzle"):
        if st.session_state.nozzles:
            to_del = st.selectbox("Select to Remove", list(st.session_state.nozzles.keys()))
            if st.button("Delete Permanently", type="primary", use_container_width=True):
                del st.session_state.nozzles[to_del]
                st.rerun()
