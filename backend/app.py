# backend/app.py
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from humaniser import humanise_text, init_model

def create_app():
    app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
    CORS(app)

    # Optionally initialize model on startup (comment/uncomment based on memory/time)
    if os.getenv("PRELOAD_MODEL", "false").lower() in ("1", "true", "yes"):
        init_model()

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/api/humanise", methods=["POST"])
    def humanise():
        data = request.get_json() or {}
        text = data.get("text") or data.get("input") or ""
        if not isinstance(text, str):
            return jsonify({"error": "text must be a string"}), 400
        if not text.strip():
            return jsonify({"error": "text is empty"}), 400

        try:
            out = humanise_text(text)
            return jsonify({"original": text, "humanised": out})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Serve React static files
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    # For local dev
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
