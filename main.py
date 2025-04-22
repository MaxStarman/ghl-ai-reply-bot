from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load your keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GHL_API_KEY = os.environ.get('GHL_API_KEY')

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📦 Raw Webhook Data:", data)  # Debugging

    # Try to get payload, fallback to top-level
    payload = data.get("payload", data)

    # Extract contact and message fields
    contact_info = payload.get("contact") or payload.get("data", {}).get("contact") or {}
    message_data = payload.get("message") or payload.get("data", {}).get("message") or payload

    contact_id = contact_info.get("id")
    contact_name = contact_info.get("fullName", "Friend")
    incoming_msg = message_data.get("body", "")

    if not contact_id or not incoming_msg:
        print("❌ Missing contact ID or message")
        return jsonify({"error": "Missing contact ID or message"}), 400

    print("📩 Incoming Message:", incoming_msg)

    # Send to ChatGPT
    prompt = f"Reply to this email as Scott Sweet in a friendly, helpful, professional tone. Here’s the message:\n\n{incoming_msg}"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    chat_payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful email assistant replying as Scott Sweet."},
            {"role": "user", "content": prompt}
        ]
    }

    chat_response = requests.post("https://api.openai.com/v1/chat/completions", json=chat_payload, headers=headers)
    gpt_reply = chat_response.json()["choices"][0]["message"]["content"].strip()

    print("🤖 GPT Reply:", gpt_reply)

    # Send reply back via GHL API
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

    response = requests.post(ghl_url, headers=ghl_headers, json=ghl_data)
    print("📤 GHL Response:", response.status_code, response.text)

    return jsonify({"status": "sent", "gpt_reply": gpt_reply}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

