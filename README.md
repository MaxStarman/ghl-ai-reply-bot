# GHL AI Reply Bot

This project creates a lightweight webhook server that connects GoHighLevel (GHL) with ChatGPT. It automatically replies to email responses from leads or customers using AI-generated messages.

### 🔧 How It Works

1. A lead replies to your email (sent from GHL).
2. GHL triggers a webhook to this app.
3. This server:
   - Receives the webhook
   - Extracts the customer's message
   - Sends it to ChatGPT (OpenAI)
   - Gets a smart, relevant reply
   - Sends the reply back to the contact via GHL API

### 🧠 Tech Stack

- Python (Flask)
- OpenAI API (ChatGPT)
- GoHighLevel API (for sending replies)
- Hosted on [Render](https://render.com)

### 🔑 Environment Variables

This project uses the following secrets:

| Variable           | Description                         |
|--------------------|-------------------------------------|
| `OPENAI_API_KEY`   | Your ChatGPT API key from OpenAI    |
| `GHL_API_KEY`      | Your GoHighLevel API key            |

### 🚀 How to Deploy

1. Fork or clone this repo
2. Deploy to Render as a Web Service (point to `main.py`)
3. Add your API keys as environment variables
4. In GHL, create a workflow with a trigger:
   - **Trigger:** Customer Replied (email)
   - **Action:** Webhook → your Render app URL
5. Your bot will now reply automatically!

---

### 🔥 Created by Scott Sweet
For use with AI-assisted affiliate marketing automation 🚀


