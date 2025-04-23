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
        location_id = data.get("location", {}).get("id")
        contact_email = data.get("email")

        if not user_message or not contact_id or not location_id or not contact_email:
            return jsonify({"error": "Missing required fields (message, contact_id, location_id, or email)"}), 400

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

        email_payload = {
            "to": contact_email,
            "from": "scott@lc.hbquarters.com",
            "locationId": location_id,
            "subject": "RE: Your Question",
            "body": reply,
            "contactId": contact_id
        }

        print("📧 Payload to GHL /emails/send endpoint:", email_payload)

        ghl_response = requests.post(
            "https://rest.gohighlevel.com/v1/emails/send",
            json=email_payload,
            headers=headers
        )

        print("📤 GHL response status:", ghl_response.status_code)
        print("📤 GHL response text:", ghl_response.text)

        return jsonify({"status": "sent", "emailBody": reply})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

# Run the app on the correct port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
