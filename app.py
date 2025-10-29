from flask import Flask, request, jsonify
app = Flask(__name__)

@app.get("/")
def root():
    return "OK", 200

@app.get("/slack/delphi")
def delphi_get():
    return "OK /slack/delphi", 200

@app.post("/slack/delphi")
def delphi_post():
    text = (request.form.get("text") or "").strip()
    return jsonify({
        "response_type": "ephemeral",
        "text": f"You said: {text or 'Hello from Delphi 👋'}"
    })
