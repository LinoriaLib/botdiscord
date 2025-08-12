from flask import Flask, request, jsonify

app = Flask(__name__)

commands = []
player_count = 0
banned_user_ids = set()


@app.route("/")
def index():
    return "Flask server is running!"


@app.route("/send_command", methods=["POST"])
def send_command():
    data = request.json
    print(f"Get commands Discord bot: {data}") #u can remove this line if u want
    commands.append(data)
    return jsonify({"status": "OK"})
    
@app.route("/get_commands", methods=["GET"])
def get_commands():
    return jsonify(commands)


@app.route("/clear_commands", methods=["POST"])
def clear_commands():
    commands.clear()
    return jsonify({"status": "cleared"})


@app.route("/update_players", methods=["POST"])
def update_players():
    global player_count
    data = request.json
    player_count = data.get("count", 0)
    print(f"Players: {player_count}")
    return jsonify({"status": "updated"})


@app.route("/get_players")
def get_players():
    return jsonify({"count": player_count})


# === BAN SYSTEM ===


@app.route("/is_banned/<int:user_id>")
def is_banned(user_id):
    return jsonify({"banned": user_id in banned_user_ids})


@app.route("/ban", methods=["POST"])
def ban():
    data = request.json
    user_id = data.get("user_id")
    if user_id is not None:
        banned_user_ids.add(int(user_id))
        print(f"✅ Banned UserId: {user_id}")
        return jsonify({"status": "banned"})
    return jsonify({"error": "Missing user_id"}), 400


@app.route("/unban", methods=["POST"])
def unban():
    data = request.json
    user_id = data.get("user_id")
    if user_id is not None:
        banned_user_ids.discard(int(user_id))
        print(f"✅ Unbanned UserId: {user_id}")
        return jsonify({"status": "unbanned"})
    return jsonify({"error": "Missing user_id"}), 400


def run():
    app.run(host="0.0.0.0", port=5000)

# MADE BY DAI VIET
