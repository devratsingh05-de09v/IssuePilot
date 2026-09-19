from flask import Flask, request, jsonify, send_from_directory
import os
from flask_cors import CORS
from datetime import datetime

from storage import create_case, get_case, upload_evidence, set_diagnosis, resolve_case
from bedrock import diagnose

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

@app.route("/", methods=["GET"])
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")

# Temporary in-memory storage.
# Later this will become DynamoDB.



@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "IssuePilot"
    })


@app.route("/cases", methods=["POST"])
def create_case_route():
    data = request.get_json(silent=True)

    if not data or not data.get("problem"):
        return jsonify({
            "success": False,
            "error": "Please describe your problem."
        }), 400

    case = create_case(data["problem"])

    return jsonify({
        "success": True,
        "case": case
    }), 201


@app.route("/cases/<case_id>", methods=["GET"])
def get_case_route(case_id):
    case = get_case(case_id)

    if not case:
        return jsonify({
            "success": False,
            "error": "Case not found."
        }), 404

    return jsonify({
        "success": True,
        "case": case
    })


@app.route("/cases/<case_id>/evidence", methods=["POST"])
def add_evidence_route(case_id):
    case = get_case(case_id)

    if not case:
        return jsonify({"success": False, "error": "Case not found."}), 404

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No evidence file received."}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    evidence = upload_evidence(case_id, file)

    return jsonify({
        "success": True,
        "case_id": case_id,
        "evidence": evidence
    })


@app.route("/cases/<case_id>/diagnose", methods=["POST"])
def diagnose_case(case_id):
    case = get_case(case_id)

    if not case:
        return jsonify({
            "success": False,
            "error": "Case not found."
        }), 404

    diagnosis = diagnose(case["problem"], case.get("evidence", []))

    updated_case = set_diagnosis(case_id, diagnosis)

    return jsonify({
        "success": True,
        "case": updated_case
    })

@app.route("/cases/<case_id>/resolve", methods=["POST"])
def resolve_case_route(case_id):

    case = get_case(case_id)

    if not case:
        return jsonify({
            "success": False,
            "error": "Case not found."
        }), 404

    case = resolve_case(case_id)

    return jsonify({
        "success": True,
        "case": case
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )