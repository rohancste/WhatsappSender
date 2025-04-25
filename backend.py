import gspread
import time
from typing import List, Dict, Optional
from enhanced_sender import EnhancedWAHAClient
import random

class WhatsAppSender:
    def __init__(self, credentials_file: str = "service_account.json"):
        self.client = EnhancedWAHAClient()
        self.gc = gspread.service_account(filename=credentials_file)
        self.worksheet = None
        self.data = []
        self.headers = []

    def connect_to_sheet(self, sheet_url: str, worksheet_index: int = 0) -> bool:
        try:
            workbook = self.gc.open_by_url(sheet_url)
            self.worksheet = workbook.get_worksheet(worksheet_index)
            self.headers = self.worksheet.row_values(1)
            return True
        except Exception as e:
            print(f"Error connecting to sheet: {e}")
            return False

    def load_data(self) -> List[Dict]:
        try:
            self.data = self.worksheet.get_all_records()
            return self.data
        except Exception as e:
            print(f"Error loading data: {e}")
            return []

    def detect_columns(self) -> Dict[str, str]:
        # ... (same as before)
        column_mapping = {}
        name_keywords = ["name", "customer", "client", "person"]
        phone_keywords = ["phone", "mobile", "contact", "number", "cell"]
        message_keywords = ["message", "text", "content", "msg"]
        status_keywords = ["status", "sent", "delivered"]
        for header in self.headers:
            header_lower = header.lower()
            if any(keyword in header_lower for keyword in name_keywords):
                column_mapping["name"] = header
            if any(keyword in header_lower for keyword in phone_keywords):
                column_mapping["phone"] = header
            if any(keyword in header_lower for keyword in message_keywords):
                column_mapping["message"] = header
            if any(keyword in header_lower for keyword in status_keywords):
                column_mapping["status"] = header
        return column_mapping

    def send_messages(self, column_mapping: Dict[str, str], status_column: str = "Status", typing_time: int = 2, min_delay: int = 1, max_delay: int = 10) -> list:
        results = []
        if not self.data:
            results.append("No data loaded. Call load_data() first.")
            return results
        if "phone" not in column_mapping or "message" not in column_mapping:
            results.append("Missing required columns (phone or message)")
            return results
        if status_column not in self.headers:
            self.worksheet.update_cell(1, len(self.headers) + 1, status_column)
            self.headers.append(status_column)
        status_col_idx = self.headers.index(status_column) + 1
        for idx, row in enumerate(self.data, start=2):
            current_status = row.get(status_column, "")
            if current_status == "Sent":
                results.append(f"Row {idx}: Already sent, skipping")
                continue
            phone = str(row[column_mapping["phone"]])
            message = row[column_mapping["message"]]
            if "name" in column_mapping and row[column_mapping["name"]]:
                name = row[column_mapping["name"]]
                message = message.replace("{name}", name)
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 10:
                results.append(f"Row {idx}: Invalid phone number, skipping")
                self.worksheet.update_cell(idx, status_col_idx, "Invalid Phone")
                continue
            results.append(f"Sending message to {phone}")

            # --- Randomized Typing Delay ---
            typing_delay = random.uniform(1.5, 4.0)
            results.append(f"Typing delay: {typing_delay:.2f} seconds")
            time.sleep(typing_delay)

            self.worksheet.update_cell(idx, status_col_idx, "Sending")
            result = self.client.send_message_with_typing(phone, message, typing_time)
            if result and (result.get("sent") or "_data" in result or "id" in result):
                status = "Sent"
            else:
                status = "Failed"
            self.worksheet.update_cell(idx, status_col_idx, status)
            results.append(f"Row {idx}: Message {status}")

            # --- Randomized Delay Between Messages (user input range) ---
            message_gap = random.uniform(min_delay, max_delay)
            results.append(f"Waiting {message_gap:.2f} seconds before next message")
            time.sleep(message_gap)
        return results