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
    waha_url = st.text_input("WAHA Server URL", value="http://54.226.226.61:3000")
    st.caption("Session: `hiring-cste` (default)")

    # --- Test WAHA Connection ---
    if st.button("Test WAHA Connection"):
        import requests
        try:
            response = requests.get(f"{waha_url}/api/sessions", timeout=10)
            if response.status_code == 200:
                st.success("WAHA server is ONLINE!")
                # st.write(response.text)  # <-- Remove or comment out this line
            else:
                st.error(f"WAHA server is OFFLINE. Status code: {response.status_code}")
        except Exception as e:
            st.error(f"Error connecting to WAHA server: {e}")

    # --- Send Test Message ---
    st.markdown("**Send Test WhatsApp Message**")
    test_phone = st.text_input("Test Phone Number")
    test_message = st.text_area("Test Message", value="This is a test message from WhatsApp Sender. If you received this, the connection is working! 👍")
    test_typing_time = st.number_input("Typing Time (seconds)", min_value=1, value=2, key="test_typing_time")
    if st.button("Send Test Message"):
        from enhanced_sender import EnhancedWAHAClient
        import re
        if not test_phone:
            st.warning("Please enter a test phone number.")
        elif not test_message.strip():
            st.warning("Please enter a message to send.")
        else:
            # Remove all non-digit characters
            phone_clean = re.sub(r'\D', '', test_phone)
            # Strict validation for Indian numbers (country code 91)
            if not phone_clean.startswith("91"):
                st.warning("Please include the country code (e.g., 91XXXXXXXXXX for India) at the beginning of the phone number.")
            elif len(phone_clean) != 12:
                st.warning("Phone number must be exactly 12 digits (country code + 10 digit number). Example: 91XXXXXXXXXX")
            elif not phone_clean.isdigit():
                st.warning("Phone number must contain only digits.")
            else:
                client = EnhancedWAHAClient(base_url=waha_url)
                with st.spinner("Sending test message..."):
                    result = client.send_message_with_typing(test_phone, test_message, test_typing_time)
                if result and (result.get("sent") or "_data" in result or "id" in result):
                    st.success("Test message sent successfully!")
                    # st.write(result)  # <-- Remove or comment out this line
                else:
                    st.error(f"Failed to send test message: {result}")

# --- Sheet Details Section ---
with st.expander("3️⃣ Google Sheet Details", expanded=True):
    sheet_url = st.text_input("Google Sheet URL")
    worksheet_index = st.number_input("Worksheet Index (0 for first sheet)", min_value=0, value=0)

# --- Message Settings ---
with st.expander("4️⃣ Message Settings", expanded=True):
    typing_time = st.number_input("Typing Time (seconds)", min_value=1, value=2)
    min_delay = st.number_input("Min Delay Between Messages (seconds)", min_value=1, value=1)
    max_delay = st.number_input("Max Delay Between Messages (seconds)", min_value=1, value=10)

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
            results = sender.send_messages(
                column_mapping,
                typing_time=typing_time,
                min_delay=min_delay,
                max_delay=max_delay
            )
            st.success("Message sending completed!")
        st.write("### Log")
        for r in results:
            st.write(r)