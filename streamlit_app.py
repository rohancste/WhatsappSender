import streamlit as st
from backend import WhatsAppSender

st.set_page_config(page_title="Cloud WhatsApp Sender", page_icon=":rocket:", layout="wide")

# Sidebar for branding/instructions
with st.sidebar:
    st.image("https://img.icons8.com/color/96/whatsapp--v1.png", width=80)
    st.title("WhatsApp Sender")
    st.markdown("""
    - Send WhatsApp messages from Google Sheets
    - No installation required
    - Powered by WAHA API
    """)
    st.info("Fill the form and click **Connect & Detect Columns** to begin.")

st.title("📤 Cloud WhatsApp Sender")

# --- Credentials Section ---
with st.expander("1️⃣ Google Sheets Credentials", expanded=True):
    credentials_file = st.text_input("Service Account JSON Path", value="service_account.json", help="Upload your Google service account JSON file.")
    uploaded_file = st.file_uploader("Or upload Service Account JSON", type="json")
    if uploaded_file:
        # Save uploaded file to disk
        with open("uploaded_service_account.json", "wb") as f:
            f.write(uploaded_file.read())
        credentials_file = "uploaded_service_account.json"
        st.success("Service account file uploaded.")

# --- WAHA Server Section ---
with st.expander("2️⃣ WAHA Server Configuration", expanded=True):
    waha_url = st.text_input("WAHA Server URL", value="http://23.23.209.128")
    st.caption("Session: `hiring-cste` (default)")

# --- Sheet Details Section ---
with st.expander("3️⃣ Google Sheet Details", expanded=True):
    sheet_url = st.text_input("Google Sheet URL")
    worksheet_index = st.number_input("Worksheet Index (0 for first sheet)", min_value=0, value=0)

# --- Message Settings ---
with st.expander("4️⃣ Message Settings", expanded=True):
    typing_time = st.number_input("Typing Time (seconds)", min_value=1, value=2)

# --- Connect & Detect Columns ---
if st.button("🔍 Connect & Detect Columns"):
    sender = WhatsAppSender(credentials_file)
    if sender.connect_to_sheet(sheet_url, worksheet_index):
        sender.load_data()
        columns = sender.detect_columns()
        st.session_state['sender'] = sender
        st.session_state['columns'] = columns
        st.success(f"Detected columns: {columns}")
    else:
        st.error("Failed to connect to sheet. Check credentials and sheet URL.")

# --- Column Mapping & Send Messages ---
if 'columns' in st.session_state:
    st.subheader("🗂️ Column Mapping")
    col1, col2, col3 = st.columns(3)
    with col1:
        name_col = st.text_input("Name Column", value=st.session_state['columns'].get("name", ""))
    with col2:
        phone_col = st.text_input("Phone Column", value=st.session_state['columns'].get("phone", ""))
    with col3:
        message_col = st.text_input("Message Column", value=st.session_state['columns'].get("message", ""))

    if st.button("🚀 Send WhatsApp Messages"):
        sender = st.session_state['sender']
        column_mapping = {"name": name_col, "phone": phone_col, "message": message_col}
        with st.spinner("Sending messages..."):
            results = sender.send_messages(column_mapping, typing_time=typing_time)
            st.success("Message sending completed!")
        st.write("### Log")
        for r in results:
            st.write(r)