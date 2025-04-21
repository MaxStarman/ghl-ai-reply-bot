from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Load your keys from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GHL_API_KEY = os.environ.get('GHL_API_KEY')

@app.route("/", methods=["GET"])
def home():
    return "GHL AI Bot is Live!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # Extract contact info and message
    contact_id = data.get("contact", {}).get("id")
    contact_name = data.get("contact", {}).get("fullName", "Friend")
    incoming_msg = data.get("body", "")

    print("📩 Incoming Message:", incoming_msg)

    if not contact_id or not incoming_msg:
        return jsonify({"error": "Missing contact ID or message"}), 400

    # Send to ChatGPT
    prompt = f"Reply to this email as Scott Sweet in a friendly, helpful, professional tone. Here’s the message:\n\n{incoming_msg}"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful email assistant replying as Scott Sweet."},
            {"role": "user", "content": prompt}
        ]
    }

    chat_response = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
    gpt_reply = chat_response.json()["choices"][0]["message"]["content"].strip()

    print("🤖 GPT Reply:", gpt_reply)

    # Send reply back via GHL API
    ghl_url = f"https://rest.gohighlevel.com/v1/conversations/messages"
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

    return jsonify({"status": "sent", "gpt_reply": gpt_reply}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
