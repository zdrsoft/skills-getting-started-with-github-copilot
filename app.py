from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample activities data structure
activities = {
    "yoga": {
        "description": "Morning yoga session",
        "schedule": "7:00 AM - 8:00 AM",
        "max_participants": 10,
        "participants": [],
    },
    "cooking-class": {
        "description": "Learn to cook Italian cuisine",
        "schedule": "5:00 PM - 8:00 PM",
        "max_participants": 15,
        "participants": [],
    },
}

@app.route("/activities", methods=["GET"])
def get_activities():
    return jsonify(activities)

@app.route("/activities/<activity_name>/signup", methods=["POST"])
def signup(activity_name):
    email = request.args.get("email")
    username = request.args.get("username")  # <-- new
    if not email:
        return jsonify(detail="Email is required"), 400

    activity = activities.get(activity_name)
    if not activity:
        return jsonify(detail="Activity not found"), 404

    # helper to check existing emails in participants (support strings or dicts)
    def email_in_participants(email, participants):
        for p in participants:
            if isinstance(p, dict):
                if p.get("email") == email:
                    return True
            elif p == email:
                return True
        return False

    if email_in_participants(email, activity["participants"]):
        return jsonify(detail="Already signed up"), 400

    # store participant as an object to include username if provided
    participant_entry = {"email": email, "username": username} if username else {"email": email}
    activity["participants"].append(participant_entry)

    return jsonify(message="Signed up successfully", participant=participant_entry), 200