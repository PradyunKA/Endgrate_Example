from flask import Flask, render_template, request, jsonify, redirect, session
import requests
import os
from dotenv import load_dotenv



load_dotenv()  # Load environment variables from .env file


SECRET_KEY = "SECRET_KEY"
ENDGRATE_API_KEY = "ENDGRATE_API_KEY"
APPLICATION_URL = "APPLICATION_URL"

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

    print(f"Data Retrieved: {data}")  # Check the data fetched

    formatted_data = []
    if 'transfer_data' in data:
        for item in data['transfer_data']:
            entry = item['data']
            # Flatten email addresses (assuming only one per entry for simplicity)
            email_info = entry['email_addresses'][0] if entry['email_addresses'] else {}
            formatted_data.append({
                'email_address': email_info.get('email_address', 'N/A'),
                'email_type': email_info.get('email_type', 'N/A'),
                'first_name': entry['name'].split()[0] if 'name' in entry and entry['name'] else 'N/A',
                'last_name': entry['name'].split()[1] if 'name' in entry and len(entry['name'].split()) > 1 else 'N/A',
                'is_active': 'Yes' if entry.get('is_active', False) else 'No'
            })
    else:
        print("No transfer_data found")

    return formatted_data 

@app.route('/view-data')
def view_data():
    data = get_endgrate_data()  # Fetch and format data using your function
    print(f"Formatted Data sent to template: {data}")  # Debug to see what's sent to the frontend
    return render_template('data_display.html', data=data)




@app.route('/auth')
def auth():
    global ENDGRATE_SESSION_ID
    return redirect(f"https://endgrate.com/session?session_id={ENDGRATE_SESSION_ID}")


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
