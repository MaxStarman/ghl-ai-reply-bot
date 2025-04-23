import os
from flask import Flask, request, jsonify
import openai
import requests

# Set up Flask app
app = Flask(__name__)

# Set your API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
ghl_api_key = os.getenv("GHL_API_KEY")

# Define the route to receive webhook events
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("🚀 Incoming data:", data)

        user_message = data.get("message", {}).get("body", "")
        contact_id = data.get("contact_id")
        contact_email = data.get("email")
        location_id = data.get("location", {}).get("id")

        if not user_message or not contact_id or not contact_email or not location_id:
            return jsonify({"error": "Missing message, contact_id, email, or location_id"}), 400

        messages = [
            {"role": "system", "content": "You are a helpful affiliate marketer responding to messages."},
            {"role": "user", "content": user_message}
        ]

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        reply = response.choices[0].message.content
        print("✅ GPT Reply:", reply)

        headers = {
            "Authorization": f"Bearer {ghl_api_key}",
            "Content-Type": "application/json"
        }

        message_payload = {
            "locationId": location_id,
            "contactId": contact_id,
            "type": "Email",
            "direction": "outgoing",
            "email": {
                "to": contact_email,
                "from": "scott@lc.hbquarters.com",
                "subject": "Reply from Scott",
                "body": reply,
                "send": True
            }
        }

        print("📦 Payload to GHL:", message_payload)

        ghl_response = requests.post(
            "https://rest.gohighlevel.com/v1/conversations/messages",
            json=message_payload,
            headers=headers
        )

        print("📧 GHL response status:", ghl_response.status_code)
        print("📧 GHL response text:", ghl_response.text)

        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

# Run the app on the correct port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
