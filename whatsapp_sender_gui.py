import gspread
import time
import json
import os
import requests  # Add this import for the HTTP requests
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Optional, Any
from enhanced_sender import EnhancedWAHAClient

class WhatsAppSenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Sender")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.sender = None
        self.create_widgets()
        
    def create_widgets(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Credentials section
        cred_frame = ttk.LabelFrame(main_frame, text="Google Sheets Credentials", padding="10")
        cred_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(cred_frame, text="Service Account JSON:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.cred_path = tk.StringVar(value="service_account.json")
        ttk.Entry(cred_frame, textvariable=self.cred_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(cred_frame, text="Browse", command=self.browse_credentials).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(cred_frame, text="Connect", command=self.connect_to_sheets).grid(row=0, column=3, padx=5, pady=5)
        
        # Add WAHA configuration section
        self.create_waha_config_section(main_frame)
        
        # Sheet details section
        sheet_frame = ttk.LabelFrame(main_frame, text="Google Sheet Details", padding="10")
        sheet_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(sheet_frame, text="Sheet URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sheet_url = tk.StringVar()
        ttk.Entry(sheet_frame, textvariable=self.sheet_url, width=50).grid(row=0, column=1, columnspan=3, padx=5, pady=5)
        
        ttk.Label(sheet_frame, text="Worksheet Index:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.worksheet_index = tk.StringVar(value="0")
        ttk.Entry(sheet_frame, textvariable=self.worksheet_index, width=5).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(sheet_frame, text="Connect to Sheet", command=self.connect_to_sheet).grid(row=1, column=2, padx=5, pady=5)
        
        # Column mapping section
        column_frame = ttk.LabelFrame(main_frame, text="Column Mapping", padding="10")
        column_frame.pack(fill=tk.X, pady=5)
        
        self.column_mapping_text = tk.Text(column_frame, height=5, width=50)
        self.column_mapping_text.pack(fill=tk.X, pady=5)
        self.column_mapping_text.insert(tk.END, "Connect to a sheet to detect columns...")
        self.column_mapping_text.config(state=tk.DISABLED)
        
        # Message sending section
        send_frame = ttk.LabelFrame(main_frame, text="Send Messages", padding="10")
        send_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(send_frame, text="Typing Time (seconds):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.typing_time = tk.StringVar(value="2")
        ttk.Entry(send_frame, textvariable=self.typing_time, width=5).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(send_frame, text="Send Messages", command=self.send_messages).grid(row=0, column=2, padx=5, pady=5)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar to log
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
    def browse_credentials(self):
        filename = filedialog.askopenfilename(
            title="Select Service Account JSON",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filename:
            self.cred_path.set(filename)
    
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def connect_to_sheets(self):
        try:
            self.sender = WhatsAppSender(self.cred_path.get())
            self.log("Connected to Google Sheets API")
        except Exception as e:
            self.log(f"Error connecting to Google Sheets API: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect to Google Sheets API: {e}")
    
    def connect_to_sheet(self):
        if not self.sender:
            messagebox.showerror("Error", "Please connect to Google Sheets API first")
            return
        
        try:
            sheet_url = self.sheet_url.get()
            worksheet_index = int(self.worksheet_index.get())
            
            if not sheet_url:
                messagebox.showerror("Error", "Please enter a sheet URL")
                return
            
            success = self.sender.connect_to_sheet(sheet_url, worksheet_index)
            
            if success:
                self.log(f"Connected to worksheet: {self.sender.worksheet.title}")
                self.log(f"Headers: {self.sender.headers}")
                
                # Load data
                self.sender.load_data()
                self.log(f"Loaded {len(self.sender.data)} records")
                
                # Detect columns
                column_mapping = self.sender.detect_columns()
                
                # Update column mapping text
                self.column_mapping_text.config(state=tk.NORMAL)
                self.column_mapping_text.delete(1.0, tk.END)
                for col_type, col_name in column_mapping.items():
                    self.column_mapping_text.insert(tk.END, f"{col_type}: {col_name}\n")
                self.column_mapping_text.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Connection Error", "Failed to connect to the specified sheet")
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def create_waha_config_section(self, parent):
        """Create WAHA server configuration section"""
        waha_frame = ttk.LabelFrame(parent, text="WAHA Server Configuration")
        waha_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # WAHA Server URL
        ttk.Label(waha_frame, text="Server URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.waha_url = tk.StringVar(value="http://23.23.209.128")  # Default from EnhancedWAHAClient
        ttk.Entry(waha_frame, textvariable=self.waha_url, width=40).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Note about session name
        ttk.Label(waha_frame, text="Note: Using session 'hiring-cste'").grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Test phone number for direct message test
        ttk.Label(waha_frame, text="Test Phone:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.test_phone = tk.StringVar(value="")
        ttk.Entry(waha_frame, textvariable=self.test_phone, width=40).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(waha_frame)
        button_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Test Connection", command=self.test_waha_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Send Test Message", command=self.send_test_message).pack(side=tk.LEFT, padx=5)

    def send_test_message(self):
        """Send a test message to verify WAHA is working"""
        phone = self.test_phone.get().strip()
        if not phone:
            messagebox.showerror("Error", "Please enter a test phone number")
            return
        
        try:
            self.log(f"Sending test message to {phone}...")
            
            # Create a client with the current URL from GUI
            client = EnhancedWAHAClient(base_url=self.waha_url.get())
            
            # Get typing time
            try:
                typing_time = int(self.typing_time.get())
            except ValueError:
                typing_time = 2
            
            # Send a simple test message
            result = client.send_message_with_typing(
                phone, 
                "This is a test message from WhatsApp Sender. If you received this, the connection is working! 👍",
                typing_time=typing_time
            )
            
            if result and result.get("sent"):
                self.log(f"Test message sent successfully: {result}")
                messagebox.showinfo("Success", "Test message sent successfully!")
            else:
                self.log(f"Failed to send test message: {result}")
                messagebox.showerror("Error", f"Failed to send test message: {result}")
        except Exception as e:
            self.log(f"Error sending test message: {e}")
            messagebox.showerror("Error", f"Error sending test message: {e}")

    def test_waha_connection(self):
        """Test connection to WAHA server"""
        try:
            self.log(f"Testing connection to WAHA server at {self.waha_url.get()}...")
            
            # First, try a simple GET request to check if server is reachable
            # Add timeout to prevent hanging
            response = requests.get(f"{self.waha_url.get()}/api/sessions", timeout=10)
            
            if response.status_code == 200:
                self.log(f"Server is reachable. Status code: {response.status_code}")
                self.log(f"Response: {response.text[:200]}...")  # Log first 200 chars
                
                # Now test if we can use the session
                # Create client with URL from GUI
                client = EnhancedWAHAClient(base_url=self.waha_url.get())
                
                # Try a simple operation like checking if the session exists
                # Use the hardcoded session name from EnhancedWAHAClient
                test_payload = {
                    "session": "hiring-cste"
                }
                
                # Make a direct request to check session status
                session_response = requests.post(
                    f"{self.waha_url.get()}/api/sessions/status", 
                    json=test_payload,
                    timeout=10
                )
                
                self.log(f"Session status response: {session_response.status_code}")
                self.log(f"Session status: {session_response.text}")
                
                if session_response.status_code == 200:
                    session_data = session_response.json()
                    self.log(f"Session data: {session_data}")
                    
                    if session_data.get("status") == "CONNECTED":
                        self.log("WAHA session is active and connected!")
                        messagebox.showinfo("Success", "WAHA server is ONLINE and session is CONNECTED!")
                    else:
                        self.log(f"Session exists but status is: {session_data.get('status')}")
                        messagebox.showwarning("Warning", f"WAHA server is ONLINE but session status is: {session_data.get('status')}")
                else:
                    self.log("Session check failed")
                    messagebox.showwarning("Warning", "WAHA server is ONLINE but session check failed")
            else:
                self.log(f"Failed to connect to WAHA server: Status code {response.status_code}")
                messagebox.showerror("Connection Error", f"WAHA Server is OFFLINE. Status code: {response.status_code}")
        except requests.exceptions.Timeout:
            self.log("Connection timed out. Server might be down or unreachable.")
            messagebox.showerror("Connection Error", "WAHA Server is OFFLINE (Connection timed out)")
        except requests.exceptions.ConnectionError:
            self.log("Connection error. Server might be down or unreachable.")
            messagebox.showerror("Connection Error", "WAHA Server is OFFLINE (Connection error)")
        except Exception as e:
            self.log(f"Error connecting to WAHA server: {e}")
            messagebox.showerror("Connection Error", f"Error connecting to WAHA server: {e}")

    def send_messages(self):
        if not self.sender or not self.sender.worksheet:
            messagebox.showerror("Error", "Please connect to a sheet first")
            return
        
        try:
            # Get column mapping
            column_mapping = {}
            mapping_text = self.column_mapping_text.get(1.0, tk.END)
            for line in mapping_text.strip().split('\n'):
                if ':' in line:
                    col_type, col_name = line.split(':', 1)
                    column_mapping[col_type.strip()] = col_name.strip()
            
            if not column_mapping:
                messagebox.showerror("Error", "No column mapping detected")
                return
            
            # Get typing time
            try:
                typing_time = int(self.typing_time.get())
            except ValueError:
                typing_time = 2
                self.log("Invalid typing time, using default (2 seconds)")
            
            # Confirm before sending
            confirm = messagebox.askyesno(
                "Confirm", 
                f"This will send WhatsApp messages to {len(self.sender.data)} contacts. Continue?"
            )
            
            if not confirm:
                return
            
            # Send messages in a separate thread to keep UI responsive
            import threading
            
            def send_thread():
                try:
                    # Create a new client with the URL from GUI
                    self.sender.client = EnhancedWAHAClient(base_url=self.waha_url.get())
                    
                    self.sender.send_messages(column_mapping, typing_time=typing_time, 
                                             callback=lambda msg: self.log(msg))
                    self.log("Message sending completed")
                    messagebox.showinfo("Success", "All messages have been processed")
                except Exception as e:
                    self.log(f"Error sending messages: {e}")
                    messagebox.showerror("Error", f"An error occurred while sending messages: {e}")
            
            threading.Thread(target=send_thread).start()
            
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")


class WhatsAppSender:
    def __init__(self, credentials_file: str = "service_account.json"):
        """
        Initialize the WhatsApp sender with Google Sheets integration
        
        Args:
            credentials_file: Path to the service account credentials JSON file
        """
        # Use the EnhancedWAHAClient with the correct server URL and session
        self.client = EnhancedWAHAClient()
        self.gc = None
        self.worksheet = None
        self.data = []
        self.headers = []
        
        # Try to authenticate with Google Sheets
        self.gc = gspread.service_account(filename=credentials_file)
    
    def connect_to_sheet(self, sheet_url: str, worksheet_index: int = 0) -> bool:
        """
        Connect to a specific Google Sheet
        
        Args:
            sheet_url: The URL of the Google Sheet
            worksheet_index: Index of the worksheet to use (default: 0)
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            workbook = self.gc.open_by_url(sheet_url)
            self.worksheet = workbook.get_worksheet(worksheet_index)
            
            # Get headers
            self.headers = self.worksheet.row_values(1)
            
            return True
        except Exception as e:
            print(f"Error connecting to sheet: {e}")
            return False
    
    def load_data(self) -> List[Dict]:
        """
        Load all data from the connected worksheet
        
        Returns:
            List of dictionaries with row data
        """
        try:
            # Get all records (converts to list of dictionaries)
            self.data = self.worksheet.get_all_records()
            return self.data
        except Exception as e:
            print(f"Error loading data: {e}")
            return []
    
    def detect_columns(self) -> Dict[str, str]:
        """
        Automatically detect important columns like name, phone, etc.
        
        Returns:
            Dictionary mapping column types to actual column names
        """
        column_mapping = {}
        
        # Define possible column names for each type
        name_keywords = ["name", "customer", "client", "person"]
        phone_keywords = ["phone", "mobile", "contact", "number", "cell"]
        message_keywords = ["message", "text", "content", "msg"]
        status_keywords = ["status", "sent", "delivered"]
        
        # Check each header for matches
        for header in self.headers:
            header_lower = header.lower()
            
            # Check for name column
            if any(keyword in header_lower for keyword in name_keywords):
                column_mapping["name"] = header
            
            # Check for phone column
            if any(keyword in header_lower for keyword in phone_keywords):
                column_mapping["phone"] = header
            
            # Check for message column
            if any(keyword in header_lower for keyword in message_keywords):
                column_mapping["message"] = header
            
            # Check for status column
            if any(keyword in header_lower for keyword in status_keywords):
                column_mapping["status"] = header
        
        return column_mapping
    
    def send_messages(self, column_mapping: Dict[str, str], 
                     status_column: str = "Status", 
                     typing_time: int = 2,
                     callback=None) -> None:
        """
        Send WhatsApp messages to all contacts in the sheet
        
        Args:
            column_mapping: Dictionary mapping column types to actual column names
            status_column: Column name to update with sending status
            typing_time: Time to show typing indicator (in seconds)
            callback: Function to call with status updates
        """
        if not self.data:
            if callback:
                callback("No data loaded. Call load_data() first.")
            return
        
        # Check if required columns exist
        if "phone" not in column_mapping or "message" not in column_mapping:
            if callback:
                callback("Missing required columns (phone or message)")
            return
        
        # Add status column if it doesn't exist
        if status_column not in self.headers:
            self.worksheet.update_cell(1, len(self.headers) + 1, status_column)
            self.headers.append(status_column)
        
        status_col_idx = self.headers.index(status_column) + 1
        
        # Process each row
        for idx, row in enumerate(self.data, start=2):  # Start from row 2 (after headers)
            # Skip if already sent
            current_status = row.get(status_column, "")
            if current_status == "Sent":
                if callback:
                    callback(f"Row {idx}: Already sent, skipping")
                continue
            
            # Get phone number and message
            phone = str(row[column_mapping["phone"]])
            message = row[column_mapping["message"]]
            
            # Format name if available
            if "name" in column_mapping and row[column_mapping["name"]]:
                name = row[column_mapping["name"]]
                # Replace {name} placeholder in message if it exists
                message = message.replace("{name}", name)
            
            # Clean phone number (remove spaces, dashes, etc.)
            phone = ''.join(filter(str.isdigit, phone))
            
            # Skip if phone number is invalid
            if len(phone) < 10:
                if callback:
                    callback(f"Row {idx}: Invalid phone number, skipping")
                self.worksheet.update_cell(idx, status_col_idx, "Invalid Phone")
                continue
            
            if callback:
                callback(f"Sending message to {phone}")
            
            # Update status to "Sending"
            self.worksheet.update_cell(idx, status_col_idx, "Sending")
            
            # Send message with typing indicator
            # Note: No need to format the phone number here as EnhancedWAHAClient._format_chat_id 
            # will handle it automatically when send_message_with_typing is called
            result = self.client.send_message_with_typing(phone, message, typing_time)
            
            # Update status based on result
            if result and result.get("sent"):
                status = "Sent"
            else:
                status = "Failed"
            
            self.worksheet.update_cell(idx, status_col_idx, status)
            if callback:
                callback(f"Row {idx}: Message {status}")
            
            # Add a delay to avoid rate limiting
            time.sleep(1)


if __name__ == "__main__":
    # Set up logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("whatsapp_sender.log"),
            logging.StreamHandler()
        ]
    )
    
    root = tk.Tk()
    app = WhatsAppSenderGUI(root)
    root.mainloop()