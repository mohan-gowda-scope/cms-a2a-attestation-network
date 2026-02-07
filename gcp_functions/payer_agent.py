import functions_framework
import json
import os
import uuid
from datetime import datetime
from google.cloud import firestore
from shared.trust_registry import TrustRegistry

db = firestore.Client()

def handle_prior_auth(params):
    """
    Autonomous Prior Auth Decision Logic (GCP)
    """
    vc = params.get("verifiable_credential")
    if not vc:
        return {"status": "Denied", "reason": "Missing Verifiable Credential"}
    
    is_valid, msg = TrustRegistry.verify_proof(vc)
    if not is_valid:
        return {"status": "Denied", "reason": f"Verification Failed: {msg}"}
    
    auth_id = f"GCP-AUTH-{uuid.uuid4().hex[:8].upper()}"
    
    # Log to Payer Firestore collection
    doc_ref = db.collection('payer_authorizations').document(auth_id)
    doc_ref.set({
        "auth_id": auth_id,
        "timestamp": datetime.utcnow().isoformat(),
        "provider_id": params.get("provider_id"),
        "status": "Auto-Approved",
        "vc_id": vc.get("id")
    })
    
    return {
        "auth_id": auth_id,
        "status": "Auto-Approved",
        "notes": "Verified via CMS Trust Hub"
    }

@functions_framework.http
def payer_agent(request):
    request_json = request.get_json(silent=True)
    if not request_json or request_json.get("jsonrpc") != "2.0":
        return {"error": "Invalid Request"}, 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    if method == "request_prior_auth":
        result = handle_prior_auth(params)
        return json.dumps({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}
    
    return json.dumps({"error": "Method not found"}), 404
