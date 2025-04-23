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

        # Extract user message and contact ID
        user_message = data.get("message", {}).get("body", "")
        contact_id = data.get("contact_id")

        if not user_message:
            return jsonify({"error": "No message body found."}), 400

        # Prepare messages for GPT-4o
        messages = [
            {"role": "system", "content": "You are a helpful affiliate marketer responding to messages."},
            {"role": "user", "content": user_message}
        ]

        # Call OpenAI GPT-4o
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )

        reply = response.choices[0].message.content
        print("✅ Response:", reply)
        print("🧠 GPT full response:", response)

        # Send reply back to GHL as email
        if contact_id:
            headers = {
                "Authorization": f"Bearer {ghl_api_key}",
                "Content-Type": "application/json"
            }
            message_payload = {
                "contactId": contact_id,
                "type": "Email",
                "subject": "Reply from Scott",
                "body": reply,
                "direction": "outgoing",
                "from": "scott@lc.hbquarters.com"
            }
            ghl_response = requests.post(
                "https://rest.gohighlevel.com/v1/conversations/messages",
                json=message_payload,
                headers=headers
            )
            print("📧 Sent reply to GHL:", ghl_response.status_code, ghl_response.text)

        return jsonify({"reply": reply})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

# Run the app on the correct port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
