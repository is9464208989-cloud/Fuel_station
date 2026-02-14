import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# --- 1. CONNECTION & STATE ---
conn = st.connection("gsheets", type=GSheetsConnection)

if 'nozzles' not in st.session_state:
    st.session_state.nozzles = {"Petrol 1": "Petrol", "Diesel 1": "Diesel"}

# Load Udhaar Data from Google Sheets (Worksheet: Sheet1)
if 'udhaar_data' not in st.session_state:
    try:
        st.session_state.udhaar_data = conn.read(worksheet="Sheet1", ttl="0")
    except:
        st.session_state.udhaar_data = pd.DataFrame(columns=["Date", "Customer", "Amount", "Status"])

if 'daily_cash' not in st.session_state:
    st.session_state.daily_cash = 0.0
if 'daily_online' not in st.session_state:
    st.session_state.daily_online = 0.0
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# --- 2. THEME & HEADER ---
st.set_page_config(page_title="petrol pump", layout="centered")
today = date.today()

# --- 3. PAGE NAVIGATION ---

# --- HOME PAGE ---
if st.session_state.page == "Home":
    st.title("⛽ petrol pump")
    st.subheader(f"📅 {today.strftime('%d %B, %Y')}")
    
    total_today = st.session_state.daily_cash + st.session_state.daily_online
    st.metric(label="Total Collected Today", value=f"₹{total_today:,.2f}")

    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    if not pending_df.empty:
        st.warning(f"🔔 NOTIFICATION: {len(pending_df)} Pending entries!")
    else:
        st.success("✅ All Udhaar cleared!")

    if st.button("📊\n\nSTOCKS", use_container_width=True):
        st.session_state.page = "Stocks"; st.rerun()
    if st.button("📒\n\nUDHAAR", use_container_width=True):
        st.session_state.page = "Udhaar"; st.rerun()
    if st.button("💰\n\nCASH COLLECTED", use_container_width=True):
        st.session_state.page = "Cash_Collected"; st.rerun()
    if st.button("📜\n\nSTOCK HISTORY", use_container_width=True):
        st.session_state.page = "Stock_History"; st.rerun()
    if st.button("⚙️\n\nSETTINGS", use_container_width=True):
        st.session_state.page = "Settings"; st.rerun()

# --- CASH COLLECTED PAGE ---
elif st.session_state.page == "Cash_Collected":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"; st.rerun()
    st.header("💰 Add to Collection")
    st.info(f"Current Total: ₹{st.session_state.daily_cash + st.session_state.daily_online:,.2f}")
    with st.form("cash_form", clear_on_submit=True):
        cash_in = st.number_input("Add Cash (₹)", value=None)
        online_in = st.number_input("Add Online/UPI (₹)", value=None)
        if st.form_submit_button("ADD TO TOTAL", use_container_width=True):
            if cash_in: st.session_state.daily_cash += cash_in
            if online_in: st.session_state.daily_online += online_in
            st.session_state.page = "Home"; st.rerun()
    st.divider()
    if st.button("🗑️ RESET DAILY TOTAL", type="primary", use_container_width=True):
        st.session_state.daily_cash = 0.0; st.session_state.daily_online = 0.0; st.rerun()

# --- STOCKS PAGE (WITH AUTO-SAVE TO SHEET) ---
elif st.session_state.page == "Stocks":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"; st.rerun()
    st.header("🛢️ Nozzle Readings")
    c1, c2 = st.columns(2)
    p_rate = c1.number_input("Petrol Rate", value=None, placeholder="₹")
    d_rate = c2.number_input("Diesel Rate", value=None, placeholder="₹")

    readings = []
    for name, fuel_type in st.session_state.nozzles.items():
        with st.container(border=True):
            st.write(f"**{name} ({fuel_type})**")
            op = st.number_input(f"Opening", key=f"{name}_op", value=None)
            cl = st.number_input(f"Closing", key=f"{name}_cl", value=None)
            rate = (p_rate if p_rate else 0) if fuel_type == "Petrol" else (d_rate if d_rate else 0)
            sale = (cl if cl else 0) - (op if op else 0)
            readings.append({"Nozzle": name, "Sale": sale, "Amount": sale * rate})

    st.divider()
    st.subheader("📝 Accounting Adjustments")
    prev_cash = st.number_input("Cash in hand of Previous Day (₹)", value=None)
    rem_cash = st.number_input("Remaining Cash in hand (₹)", value=None)

    if st.button("GENERATE & SAVE REPORT", type="primary", use_container_width=True):
        st.header("📊 Final Summary")
        req_amt = sum(item['Amount'] for item in readings)
        net_collected = (st.session_state.daily_cash + st.session_state.daily_online) - (prev_cash if prev_cash else 0) + (rem_cash if rem_cash else 0)
        diff = net_collected - req_amt
        
        st.metric("Machine Required", f"₹{req_amt:,.2f}")
        st.metric("Net Collected", f"₹{net_collected:,.2f}", delta=f"{diff:,.2f}")

        status = "MATCHED"
        if diff < 0: 
            st.error(f"❌ SHORTAGE: ₹{abs(diff):,.2f}"); status = "SHORTAGE"
        elif diff > 0: 
            st.success(f"✅ EXCESS: ₹{diff:,.2f}"); status = "EXCESS"
        
        # --- SAVE TO STOCKHISTORY WORKSHEET ---
        try:
            history_df = conn.read(worksheet="StockHistory", ttl="0")
            new_entry = pd.DataFrame([{"Date": str(today), "Required_Amt": req_amt, "Collected_Amt": net_collected, "Difference": diff, "Status": status}])
            updated_history = pd.concat([history_df, new_entry], ignore_index=True)
            conn.update(worksheet="StockHistory", data=updated_history)
            st.toast("Daily Report Saved to Cloud! ☁️")
        except:
            st.error("Could not save to 'StockHistory' worksheet. Make sure it exists!")

        st.table(pd.DataFrame(readings))

# --- STOCK HISTORY VIEW ---
elif st.session_state.page == "Stock_History":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"; st.rerun()
    st.header("📜 Past Daily Reports")
    try:
        history_df = conn.read(worksheet="StockHistory", ttl="0")
        st.dataframe(history_df, use_container_width=True, hide_index=True)
    except:
        st.info("No history found. Save a report first!")

# --- UDHAAR LOGIC (CONNECTED TO GOOGLE SHEETS) ---
elif st.session_state.page == "Udhaar":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"; st.rerun()
    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    st.metric(label="Total Udhaar Left", value=f"₹{pending_df['Amount'].sum():,.2f}")
    if st.button("➕ ADD NEW UDHAAR", use_container_width=True):
        st.session_state.page = "Add_Udhaar"; st.rerun()
    if st.button("✅ CLEAR PENDING UDHAAR", use_container_width=True):
        st.session_state.page = "Clear_List"; st.rerun()

elif st.session_state.page == "Add_Udhaar":
    if st.button("⬅ BACK", use_container_width=True):
        st.session_state.page = "Udhaar"; st.rerun()
    with st.form("new_u"):
        u_cust = st.text_input("Customer Name")
        u_amt = st.number_input("Amount", value=None)
        u_date = st.date_input("Date", today)
        if st.form_submit_button("SAVE", use_container_width=True):
            if u_cust.strip() and u_amt and u_amt > 0:
                new_row = pd.DataFrame([{"Date": str(u_date), "Customer": u_cust, "Amount": u_amt, "Status": "Pending 🔴"}])
                st.session_state.udhaar_data = pd.concat([st.session_state.udhaar_data, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=st.session_state.udhaar_data)
                st.session_state.page = "Home"; st.rerun()

elif st.session_state.page == "Clear_List":
    if st.button("⬅ BACK", use_container_width=True):
        st.session_state.page = "Udhaar"; st.rerun()
    pending_df = st.session_state.udhaar_data[st.session_state.udhaar_data["Status"] == "Pending 🔴"]
    for index, row in pending_df.iterrows():
        if st.button(f"{row['Customer']} - ₹{row['Amount']}", key=f"l_{index}", use_container_width=True):
            st.session_state.confirm_id = index; st.session_state.page = "Confirm_Clear"; st.rerun()

elif st.session_state.page == "Confirm_Clear":
    idx = st.session_state.confirm_id
    row = st.session_state.udhaar_data.loc[idx]
    st.warning(f"Clear Udhaar for {row['Customer']}?")
    if st.button("YES, PAID 🟢", use_container_width=True):
        st.session_state.udhaar_data.at[idx, "Status"] = "Cleared ✅"
        conn.update(worksheet="Sheet1", data=st.session_state.udhaar_data)
        st.session_state.page = "Home"; st.rerun()
    if st.button("CANCEL", use_container_width=True):
        st.session_state.page = "Clear_List"; st.rerun()

# --- SETTINGS ---
elif st.session_state.page == "Settings":
    if st.button("⬅ BACK TO MENU", use_container_width=True):
        st.session_state.page = "Home"; st.rerun()
    with st.container(border=True):
        st.subheader("Add Nozzle")
        new_name = st.text_input("Name")
        new_type = st.selectbox("Type", ["Petrol", "Diesel"])
        if st.button("SAVE", use_container_width=True):
            if new_name: st.session_state.nozzles[new_name] = new_type; st.rerun()
    with st.container(border=True):
        st.subheader("Delete Nozzle")
        if st.session_state.nozzles:
            to_del = st.selectbox("Select", list(st.session_state.nozzles.keys()))
            if st.button("DELETE", type="primary", use_container_width=True):
                del st.session_state.nozzles[to_del]; st.rerun()
