from flask import Flask, request, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime, timezone
import os

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI")
UBIDOTS_TOKEN = os.getenv("UBIDOTS_TOKEN")
UBIDOTS_URL = os.getenv("UBIDOTS_URL")

client = MongoClient(MONGO_URI)
db = client["iot_database"]
collection = db["sensor_data"]

headers = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

@app.route("/sensor_data", methods=["POST"])
def receive_data():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"message": "No data received", "status": "error"}), 400
        
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        motion = data.get("motion")

        if temperature is None or humidity is None or motion is None:
            return jsonify({"message": "Missing sensor data", "status": "error"}), 400

        data["timestamp"] = datetime.now(timezone.utc)
        collection.insert_one(data)

        ubidots_payload = {
            "temperature": temperature,
            "humidity": humidity,
            "motion": motion
        }
        response = requests.post(UBIDOTS_URL, json=ubidots_payload, headers=headers)

        if response.status_code == 200:
            return jsonify({"message": "Data saved and sent to Ubidots and MongoDB", "status": "success"}), 201
        else:
            return jsonify({"message": "Data saved but failed to send to Ubidots", "status": "warning", "ubidots_error": response.text}), 500

    except Exception as e:
        return jsonify({"message": str(e), "status": "error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
