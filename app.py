from flask import Flask, request, jsonify
import os, requests, threading

app = Flask(__name__)

DELPHI_URL = os.getenv("DELPHI_URL")  # set this in Render → Environment

@app.get("/")
def root():
    return "OK", 200

@app.get("/slack/delphi")
def delphi_get():
    return "OK /slack/delphi", 200

def post_to_response_url(response_url, text, visibility="ephemeral"):
    payload = {
        "response_type": "in_channel" if visibility == "in_channel" else "ephemeral",
        "blocks": [{"type":"section","text":{"type":"mrkdwn","text": text}}]
    }
    try:
        requests.post(response_url, json=payload, timeout=10)
    except Exception as e:
        # nothing else we can do if this fails
        pass

def call_delphi_async(text, user_id, channel_id, response_url):
    """Run in a thread so we can ack Slack immediately."""
    if not DELPHI_URL:
        post_to_response_url(response_url, "⚠️ `DELPHI_URL` not set in Render env.")
        return
    try:
        r = requests.post(
            DELPHI_URL,
            json={"text": text, "user_id": user_id, "channel_id": channel_id},
            timeout=30,
        )
        if r.status_code != 200:
            post_to_response_url(response_url, f"Delphi error: HTTP {r.status_code}")
            return
        data = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
        reply = data.get("reply") or r.text or "(no reply)"
        visibility = data.get("visibility", "ephemeral")  # let Delphi choose if you want
        post_to_response_url(response_url, reply, visibility)
    except Exception as e:
        post_to_response_url(response_url, f"❌ Couldn’t reach Delphi: `{e}`")

@app.post("/slack/delphi")
def delphi_post():
    # Slash commands send form-encoded data
    text       = (request.form.get("text") or "").strip()
    user_id    = request.form.get("user_id")
    channel_id = request.form.get("channel_id")
    response_url = request.form.get("response_url")

    # Kick off the Delphi call in the background
    threading.Thread(
        target=call_delphi_async,
        args=(text, user_id, channel_id, response_url),
        daemon=True
    ).start()

    # Immediate ACK (ephemeral) so Slack doesn’t timeout
    return jsonify({
        "response_type": "ephemeral",
        "text": "Working on it… I’ll post the answer here in a moment."
    })

