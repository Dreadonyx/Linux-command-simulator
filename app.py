from flask import Flask, request, jsonify, render_template
from commands import execute
from filesystem import get_current_dir

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_command():
    command = request.json.get("command", "")
    output = execute(command)

    return jsonify({
        "output": output,
        "path": get_current_dir()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

