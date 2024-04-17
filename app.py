from flask import Flask, render_template, request, jsonify, redirect, session
import requests
import os
from dotenv import load_dotenv



load_dotenv()  # Load environment variables from .env file


SECRET_KEY = "41047db087918d81d34114ddb6047a81"
ENDGRATE_API_KEY = "5f2d12be-993a-42c0-957c-e3412640c485"
APPLICATION_URL = "https://94d9-108-255-199-108.ngrok-free.app"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

payload = {
    "configuration_webhook": { "endpoint": f"{APPLICATION_URL}callback" },
    "provider": "googlesheets",
    "schema": [{ "endgrate_type": "database-user" }]
}
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {ENDGRATE_API_KEY}"
}

url = "https://endgrate.com/api/session/initiate"
response = requests.post(url, json=payload, headers=headers)
response_data = response.json()
ENDGRATE_SESSION_ID = response_data.get('session_id')
print(f"Endgrate Session ID: {ENDGRATE_SESSION_ID}")

def get_endgrate_data():
    payload = {
        "session_id": ENDGRATE_SESSION_ID,
        "endgrate_type": "database-user",
        "synchronous": True
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {ENDGRATE_API_KEY}"
    }

    response = requests.post("https://endgrate.com/api/pull/transfer", json=payload, headers=headers)
    transfer_id = response.json()["transfer_id"]

    url = f"https://endgrate.com/api/pull/data?endgrate_type=database-user&transfer_id={transfer_id}"
    response = requests.get(url, headers={"accept": "application/json","authorization": f"Bearer {ENDGRATE_API_KEY}"})
    data = response.json()


@app.route('/auth')
def auth():
    global ENDGRATE_SESSION_ID
    return redirect(f"https://endgrate.com/session?session_id={ENDGRATE_SESSION_ID}")


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
