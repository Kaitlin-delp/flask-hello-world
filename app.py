from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔹 Set your Delphi webhook URL as an environment variable in Render
DELPHI_URL = os.getenv("DELPHI_URL")

@app.get("/")
def root():
    return "OK", 200

@app.get("/slack/delphi")
def delphi_get():
    return "OK /slack/delphi", 200

@app.post("/slack/delphi")
def delphi_post():
    text = (request.form.get("text") or "").strip()
    user = request.form.get("user_name", "Unknown")

    # If Delphi URL isn’t set, show a warning
    if not DELPHI_URL:
        return jsonify({
            "response_type": "ephemeral",
            "text": "⚠️ Delphi URL not set. Please add DELPHI_URL in Render environment."
        })

    try:
        # 🔹 Send the text to Delphi agent webhook
        response = requests.post(
            DELPHI_URL,
            json={"text": text, "user": user},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            reply = data.get("reply", "No reply from Delphi.")
        else:
            reply = f"Delphi returned status {response.status_code}"

    except Exception as e:
        reply = f"❌ Error contacting Delphi: {e}"

    return jsonify({
        "response_type": "ephemeral",   # or "in_channel" if you want everyone to see it
        "text": reply
    })
