import functions_framework
import json
import os
import uuid
from datetime import datetime

@functions_framework.http
def patient_agent(request):
    """
    Patient Proxy Agent: Manages VC storage and consent.
    """
    request_json = request.get_json(silent=True)
    if not request_json:
        return "Invalid Request", 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    # Mock storage for Patient VCs
    if method == "store_credential":
        vc = params.get("verifiable_credential")
        # In production, this would save to a secure personal data vault
        print(f"[Patient Agent] Received and stored VC: {vc.get('type')}")
        return json.dumps({
            "jsonrpc": "2.0",
            "result": {"status": "Stored", "patient_consent": "Active"},
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}

    if method == "get_consent_status":
        return json.dumps({
            "jsonrpc": "2.0",
            "result": {"consent_mode": "Automated", "scope": ["Trials", "Compliance"]},
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}

    return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id}), 404
