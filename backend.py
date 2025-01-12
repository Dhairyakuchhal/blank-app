import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload_event', methods=['POST'])

def upload_event():
    data = request.get_json()
    event_text = data.get("event_text", "")

    if not event_text:
        return jsonify({"error": "No event text provided"}), 400

    # Save the event to a file
    with open('events.json', 'a') as file:
        json.dump({"event_text": event_text}, file)
        file.write("\n")

    return jsonify({"message": "Event uploaded successfully"}), 200

