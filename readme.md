In the Indiamart bot, the idea is to automate engagement of the leads. 

There's a lead section, and in the previous scripts, you can see what we need to do: fetch each lead and send an appropriate reply to them. 



This will be divided into multiple phases.

PHASE1:
1. fetch and categorise lead (business/non business) in google sheets
2. send catalog message in the lead center in indiamart

The first phase will involve sending a reply on Indiamart, and updating lead on google sheet with phone number, product details etc.

<message>
Hi there!

Thanks for your message! I’m Vaibhav from CSTE International.

We deal in all sorts of fun stuff like toys, home goods, and fashion accessories. You can check out our catalog at [caaju.in](http://caaju.in/) or on Indiamart at [indiamart.com/csteinternational](http://indiamart.com/csteinternational).

We’re also a preferred brand on Amazon and do imports and exports to the US and Dubai, so you know you’re in good hands!

Could you let me know what specific items you’re interested in? I’d love to help you out!

Looking forward to hearing from you!
</message>

PHASE2: WHATSAPP INTEGRATION

The second part will be to send a message on WhatsApp using unoffical API. 
We will not be using the official WhatsApp API, but we have another API that we are already using, so we will use that.

Phase3: RAG TOOL
The last part is determining what product they are asking for. Then, we will create an RAG where the AI bot will check if we have the product in stock. It will send a WhatsApp message to US stating that this product is in stock and providing its cost price fetching the data from our warehouse sheet.

Project timelines : Total 10 days
Phase1:12th april
phase2: 15th april
phase3: 21th april 
