import os
from flask import Flask, request, jsonify
import openai

# Set up Flask app
app = Flask(__name__)

# Set your OpenAI API key from environment variable or paste your key here directly
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the route to receive webhook events
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("\U0001F680 Incoming data:", data)

        # Extract user message from the webhook payload
        user_message = data.get("message", {}).get("body", "")
        if not user_message:
            return jsonify({"error": "No message body found."}), 400

        # Prepare messages for GPT-4o
        messages = [
            {"role": "system", "content": "You are a helpful affiliate marketer responding to messages."},
            {"role": "user", "content": user_message}
        ]

        # Call OpenAI GPT-4o
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )

        reply = response.choices[0].message.content
        print("\u2705 Response:", reply)

        return jsonify({"reply": reply})

    except Exception as e:
        print("\u274C Error:", e)
        return jsonify({"error": str(e)}), 500

# Run the app on the correct port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
