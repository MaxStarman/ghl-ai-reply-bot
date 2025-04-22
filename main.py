from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GHL_API_KEY = os.environ.get("GHL_API_KEY")

# Root route for browser check
@app.route("/", methods=["GET"])
def home():
    return "GHL AI Bot is Live!", 200

# Webhook route
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📦 Full Payload Dump:", data)  # DEBUG LOG

    # Try to extract contact ID and message body from different possible formats
    payload = data.get("payload", data)
    contact = payload.get("contact") or payload.get("data", {}).get("contact") or {}
    message = payload.get("message") or payload.get("data", {}).get("message") or payload

    contact_id = contact.get("id")
    contact_name = contact.get("fullName", "Friend")
    message_body = message.get("body", "")

    # Check required fields
    if not contact_id or not message_body:
        print("❌ Missing contact ID or message")
        return jsonify({"error": "Missing contact ID or message"}), 400

    print(f"📩 Message from {contact_name}: {message_body}")

    # Create prompt for ChatGPT
    prompt = f"Reply to this email as Scott Sweet in a friendly, helpful, professional tone. Here’s the message:\n\n{message_body}"

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    gpt_payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful email assistant replying as Scott Sweet."},
            {"role": "user", "content": prompt}
        ]
    }

    # Call ChatGPT API
    response = requests.post("https://api.openai.com/v1/chat/completions", json=gpt_payload, headers=headers)
    gpt_reply = response.json()["choices"][0]["message"]["content"].strip()
    print("🤖 GPT Reply:", gpt_reply)

    # Send reply through GHL API
    ghl_url = "https://rest.gohighlevel.com/v1/conversations/messages"
    ghl_headers = {
        "Authorization": f"Bearer {GHL_API_KEY}",
        "Content-Type": "application/json"
    }

    ghl_data = {
        "contactId": contact_id,
        "message": gpt_reply,
        "type": "Email"
    }

    ghl_response = requests.post(ghl_url, headers=ghl_headers, json=ghl_data)
    print("📤 GHL Response:", ghl_response.status_code, ghl_response.text)

    return jsonify({"status": "sent", "reply": gpt_reply}), 200

# Ensure the correct port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


