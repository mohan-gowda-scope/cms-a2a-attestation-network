import functions_framework
import json
import uuid
import os
import base64
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519

# Credentialing Agent Key (Demo Seed)
# Public Key matches Registry: Q3JlZGVudGlhbGluZ19QdWJsaWNfS2V5X1BsYWNlaG9sZA==
CRED_KEY_SEED = b"cred_agent_secret_seed_32_bytes_"
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(CRED_KEY_SEED)

def verify_npi(npi):
    # Mock NPI Verification Logic
    valid_npis = ["1234567890", "9876543210"]
    return npi in valid_npis

@functions_framework.http
def credentialing_agent(request):
    request_json = request.get_json(silent=True)
    if not request_json:
        return "Invalid Request", 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    if method == "verify_practitioner":
        npi = params.get("npi")
        if not npi or not verify_npi(npi):
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32001, "message": "Invalid or Unverified NPI"},
                "id": request_id
            }), 403, {'Content-Type': 'application/json'}

        attestation_id = str(uuid.uuid4())
        issuance_date = datetime.utcnow().isoformat() + "Z"
        
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://schema.org/healthcare"
            ],
            "id": f"urn:uuid:{attestation_id}",
            "type": ["VerifiableCredential", "ProfessionalCredential"],
            "issuer": "did:web:credentialing-v1.gov",
            "issuanceDate": issuance_date,
            "credentialSubject": {
                "id": params.get("practitioner_did", "unknown"),
                "npi": npi,
                "specialization": params.get("specialization", "General Medicine"),
                "status": "Active"
            }
        }

        # Sign
        credential_bytes = json.dumps(credential).encode('utf-8')
        signature = private_key.sign(credential_bytes)
        credential["proof"] = {
            "type": "Ed25519Signature2020",
            "created": issuance_date,
            "verificationMethod": "did:web:credentialing-v1.gov#key-1",
            "proofPurpose": "assertionMethod",
            "jws": base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        }

        return json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "professional_credential": credential,
                "status": "Verified"
            },
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}

    return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id}), 404
