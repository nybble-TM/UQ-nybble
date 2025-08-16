from flask import Flask, render_template, jsonify
import json
from datetime import datetime

app = Flask(__name__)

def month_number(month_name):
    return datetime.strptime(month_name, "%B").month

@app.route("/")
def home():
    return render_template("fullcalendar.html")

@app.route("/events")
def get_events():
    with open("results.json", "r") as f:
        events = json.load(f)
    
    fc_events = []
    for event in events:
        # Convert month name to number
        month_num = month_number(event['month'])
        # Use current year or specify a year
        year = datetime.now().year
        # Ensure day is valid int
        day = int(event['day'])
        # Build ISO date string
        start_date = f"{year}-{month_num:02d}-{day:02d}"
        
        fc_events.append({
            "title": event["title"],
            "start": start_date,
            "url": "https://campus.hellorubric.com" + event["destination"],
            "extendedProps": {
                "society": event["societyname"],
                "info": event["info"]
            }
        })
    return jsonify(fc_events)

if __name__ == "__main__":
    app.run(debug=True)