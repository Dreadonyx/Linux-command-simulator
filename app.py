from flask import Flask, request, jsonify, render_template
from commands import execute
from filesystem import get_current_dir, navigate_to, current_path

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

@app.route("/nano/save", methods=["POST"])
def nano_save():
    """Save content from the nano editor."""
    filename = request.json.get("filename", "")
    content = request.json.get("content", "")
    
    if not filename:
        return jsonify({"success": False, "error": "No filename provided"})
    
    try:
        node = navigate_to(current_path)
        node[filename] = content
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

