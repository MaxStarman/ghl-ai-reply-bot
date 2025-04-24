import os
from flask import Flask, request
import openai

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("🚀 Incoming data:", data)

        user_message = data.get("message", {}).get("body", "")
        if not user_message:
            return "Missing user message", 400

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

        # Return plain text reply for better GHL compatibility
        return reply, 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        print("❌ Error:", e)
        return str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
