from flask import Flask, render_template
import json

app = Flask(__name__)

@app.route("/")
def home():
    # Load JSON file
    with open("results.json", "r") as f:
        events = json.load(f)
    # Pass events to template
    return render_template("events.html", events=events)

if __name__ == "__main__":
    app.run(debug=True)