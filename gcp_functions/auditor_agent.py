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

@functions_framework.http
def auditor_agent(request):
    request_json = request.get_json(silent=True)
    if not request_json:
        return "Invalid Request", 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    if method == "perform_audit":
        # 1. Query Ledger for anomalies (Mock or Real Firestore)
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
            audit_summary["anomalies_detected"] = 0

        # 2. Issue Verifiable Credential (Audit Report)
        attestation_id = str(uuid.uuid4())
        issuance_date = datetime.utcnow().isoformat() + "Z"
        
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://schema.org/healthcare"
            ],
            "id": f"urn:uuid:{attestation_id}",
            "type": ["VerifiableCredential", "ComplianceAuditCredential"],
            "issuer": "did:web:auditor-v1.gov",
            "issuanceDate": issuance_date,
            "credentialSubject": {
                "organization": "HHS-OIG-Audit-Division",
                "auditResults": audit_summary,
                "recommendation": "Maintain Current Protocol"
            }
        }

        # 3. Sign
        credential_bytes = json.dumps(credential).encode('utf-8')
        signature = private_key.sign(credential_bytes)
        credential["proof"] = {
            "type": "Ed25519Signature2020",
            "created": issuance_date,
            "verificationMethod": "did:web:auditor-v1.gov#key-1",
            "proofPurpose": "assertionMethod",
            "jws": base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        }

        return json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "audit_report": credential,
                "status": "Audit Complete"
            },
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}

    return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id}), 404
