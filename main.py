import os
import requests
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
GHL_API_KEY = os.getenv("GHL_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("🚀 Incoming data:", data)

        user_message = data.get("message", {}).get("body", "")
        contact_id = data.get("contact_id")

        if not user_message or not contact_id:
            return jsonify({"error": "Missing message or contact_id"}), 400

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

        # Send reply to GHL custom field using the correct field ID
        ghl_url = f"https://rest.gohighlevel.com/v1/contacts/{contact_id}"
        headers = {
            "Authorization": f"Bearer {GHL_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "customField": [
                {
                    "id": "1746058723827",
                    "value": reply
                }
            ]
        }

        update_response = requests.put(ghl_url, headers=headers, json=payload)
        print("📬 Update Response:", update_response.status_code, update_response.text)

        return jsonify({"status": "success"})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
