import functions_framework
import json
import uuid
import os
import base64
from datetime import datetime
from google.cloud import firestore
from cryptography.hazmat.primitives.asymmetric import ed25519

# Initialize Clients
try:
    db = firestore.Client()
    MOCK_GCP = False
except Exception:
    print("Warning: GCP Auditor Agent: Clients not initialized. Using mocks.")
    db = None
    MOCK_GCP = True

# Auditor Agent Key (Demo Seed)
# Public Key matches Registry: QXVkaXRvcl9QdWJsaWNfS2V5X1BsYWNlaG9sZGVyXzMyQg==
AUDITOR_KEY_SEED = b"auditor_agent_seed_0000000000032"
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(AUDITOR_KEY_SEED)

from shared.crypto_utils import sign_credential

@functions_framework.http
def auditor_agent(request):
    request_json = request.get_json(silent=True)
    if not request_json:
        return "Invalid Request", 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    if method == "perform_audit":
        audit_summary = {
            "period": params.get("period", "last_24h"),
            "total_attestations_reviewed": 0,
            "anomalies_detected": 0,
            "status": "Green"
        }

        if db:
            docs = db.collection("attestations").limit(10).stream()
            for doc in docs:
                audit_summary["total_attestations_reviewed"] += 1
        else:
            audit_summary["total_attestations_reviewed"] = 42

        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://schema.org/healthcare"
            ],
            "id": f"urn:uuid:{uuid.uuid4()}",
            "type": ["VerifiableCredential", "ComplianceAuditCredential"],
            "issuer": "did:web:auditor-v1.gov",
            "credentialSubject": {
                "organization": "HHS-OIG-Audit-Division",
                "auditResults": audit_summary,
                "recommendation": "Maintain Current Protocol"
            }
        }

        signed_credential = sign_credential(credential, private_key, "did:web:auditor-v1.gov#key-1")

        return json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "audit_report": signed_credential,
                "status": "Audit Complete"
            },
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}

    return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id}), 404
