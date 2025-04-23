import os
from flask import Flask, request, jsonify
import openai

# Set up Flask app
app = Flask(__name__)

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("🚀 Incoming data:", data)

        user_message = data.get("message", {}).get("body", "")

        if not user_message:
            return jsonify({"error": "No user message received"}), 400

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

        # Return reply in a custom object so GHL can access it
        return jsonify({
            "custom": {
                "reply": reply
            }
        })

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

# Run app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
