import requests
import json
import time
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EnhancedWAHAClient:
    def __init__(self, base_url: str = "http://23.23.209.128"):
        self.base_url = base_url
        self.session = "hiring-cste"

    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict]:
        """Make a request to WAHA API"""
        url = f"{self.base_url}/api/{endpoint}"
        try:
            # Add more detailed logging
            logger.info(f"Making request to {url} with payload: {payload}")
            
            # Add timeout to prevent hanging
            response = requests.post(url, json=payload, timeout=10)
            
            # Log the response status and content
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text[:200]}...")  # Log first 200 chars
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error in API request to {endpoint}: {e}")
            return None

    def _format_chat_id(self, chat_id: str) -> str:
        if not (chat_id.endswith('@c.us') or chat_id.endswith('@g.us')):
            return f"{chat_id}@c.us"
        return chat_id

    def send_message_with_typing(self, chat_id: str, message: str, typing_time: int = 2) -> Optional[Dict]:
        """Send a message with typing indicator"""
        chat_id = self._format_chat_id(chat_id)
        
        try:
            # Start typing
            self.start_typing(chat_id)
            
            # Wait for specified typing time
            time.sleep(typing_time)
            
            # Stop typing
            self.stop_typing(chat_id)
            
            # Send message
            result = self.send_message(chat_id, message)
        
            
            return result
            
        except Exception as e:
            logger.error(f"Error in send_message_with_typing: {e}")
            return None

    def send_message(self, chat_id: str, message: str) -> Optional[Dict]:
        """Send a message"""
        payload = {
            "chatId": self._format_chat_id(chat_id),
            "text": message,
            "session": self.session
        }
        return self._make_request("sendText", payload)

    def start_typing(self, chat_id: str) -> Optional[Dict]:
        """Start typing indicator"""
        payload = {
            "chatId": self._format_chat_id(chat_id),
            "session": self.session
        }
        return self._make_request("startTyping", payload)

    def stop_typing(self, chat_id: str) -> Optional[Dict]:
        """Stop typing indicator"""
        payload = {
            "chatId": self._format_chat_id(chat_id),
            "session": self.session
        }
        return self._make_request("stopTyping", payload)


# Test the client if run directly
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    client = EnhancedWAHAClient()
    
    # Test message
    test_number = "8287475733"  # Replace with actual number
    test_message = "Test message from Enhanced WAHA Client! 👋"
    
    print("Testing send_message_with_typing...")
    result = client.send_message_with_typing(test_number, test_message)
    print(f"Result: {result}")