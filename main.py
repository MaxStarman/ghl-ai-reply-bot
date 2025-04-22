from flask import Flask, request, jsonify
import openai
import requests
import os

app = Flask(__name__)

# Load keys from environment variables
openai.api_key = os.environ.get("OPENAI_API_KEY")
GHL_API_KEY = os.environ.get("GHL_API_KEY")
GHL_LOCATION_ID = os.environ.get("GHL_LOCATION_ID")
FROM_EMAIL = os.environ.get("FROM_EMAIL") or "scott@lc.hbquarters.com"
FROM_NAME = os.environ.get("FROM_NAME") or "Scott Sweet"

SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT") or \
    "You are Scott Sweet, a helpful and experienced affiliate marketer who replies clearly, kindly, and confidently."

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("🚀 Incoming data:", data)

        contact_id = data.get("contact_id")
        message = data.get("message")

        if not contact_id or not message:
            return jsonify({"error": "Missing contact ID or message"}), 400

        # Ask ChatGPT to generate a reply
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ]
        )
        ai_reply = completion.choices[0].message.content.strip()
        print("💬 AI Reply:", ai_reply)

        # Send the reply using the GHL API
        send_url = "https://rest.gohighlevel.com/v1/conversations/messages"
        payload = {
            "locationId": GHL_LOCATION_ID,
            "contactId": contact_id,
            "message": ai_reply,
            "type": "Email",
            "from": {
                "email": FROM_EMAIL,
                "name": FROM_NAME
            }
        }

        headers = {
            "Authorization": f"Bearer {GHL_API_KEY}",
            "Content-Type": "application/json"
        }

        ghl_response = requests.post(send_url, json=payload, headers=headers)
        print("📬 GHL Response:", ghl_response.text)

        if ghl_response.status_code == 200:
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"error": "Failed to send message to GHL", "details": ghl_response.text}), 500

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "Scott's AI Email Bot is live and replying!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
