In the Indiamart bot, the idea is to automate engagement of the leads.

There's a lead section, and in the previous scripts, you can see what we need to do: fetch each lead and send an appropriate reply to them.

This will be divided into multiple phases.

PHASE 1: Lead Fetching, Categorization, and Catalog Messaging
1. Fetch and categorize leads (business/non-business) using Google Sheets.
   - Scripts like `IndiaMart.py` and `IndiaMartDailyUpdate.py` use Selenium to scrape lead data (name, phone, email, GST, etc.) from Indiamart's message center.
   - The data is inserted/updated into Google Sheets for further processing and tracking.
2. Send catalog message in the lead center in Indiamart.
   - The catalog message template is:
     ```
     Hi there!
     
     Thanks for your message! I’m Vaibhav from CSTE International.
     
     We deal in all sorts of fun stuff like toys, home goods, and fashion accessories. You can check out our catalog at [caaju.in](http://caaju.in/) or on Indiamart at [indiamart.com/csteinternational](http://indiamart.com/csteinternational).
     
     We’re also a preferred brand on Amazon and do imports and exports to the US and Dubai, so you know you’re in good hands!
     
     Could you let me know what specific items you’re interested in? I’d love to help you out!
     
     Looking forward to hearing from you!
     ```
   - The message is sent via Indiamart's lead center using Selenium automation.

PHASE 2: WhatsApp Integration (Unofficial API)
- After leads are processed and categorized in Google Sheets, WhatsApp outreach is automated using the WAHA API (unofficial WhatsApp API).
- The workflow:
  1. Google Sheets is used as the source of truth for leads and message templates.
  2. The `whatsapp_sender_gui.py`, `backend.py`, and `enhanced_sender.py` scripts handle:
     - Connecting to Google Sheets (via service account).
     - Detecting columns (name, phone, message, status).
     - Sending personalized WhatsApp messages to each lead using the WAHA API.
     - Updating the status in Google Sheets (Sent, Failed, Invalid Phone, etc.).
     - Typing indicators and randomized delays are used to mimic human behavior and avoid rate limiting.
- The WhatsApp message can be customized and uses placeholders (e.g., `{name}`) for personalization.
- All API credentials and server URLs are configurable in the GUI or Streamlit app.

Project timelines: Total 10 days
- Phase 1: 12th April
- Phase 2: 15th April
- Phase 3: 21st April

Note: The official WhatsApp API is NOT used; the integration relies on an existing, unofficial API (WAHA).

Phase3: RAG TOOL
The last part is determining what product they are asking for. Then, we will create an RAG where the AI bot will check if we have the product in stock. It will send a WhatsApp message to US stating that this product is in stock and providing its cost price fetching the data from our warehouse sheet.
