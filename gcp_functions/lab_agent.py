import functions_framework
import json
import uuid
import os
import base64
from datetime import datetime
from google.cloud import firestore
import google.cloud.aiplatform as aiplatform
from vertexai.generative_models import GenerativeModel, Part
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from shared.trust_registry import TrustRegistry

# Initialize Clients
try:
    db = firestore.Client()
    aiplatform.init(project=os.environ.get('GCP_PROJECT'), location='us-central1')
    model = GenerativeModel("gemini-1.5-flash-001")
    MOCK_GCP = False
except Exception:
    print("Warning: GCP Lab Agent: Clients not initialized. Using mocks.")
    db = None
    model = None
    MOCK_GCP = True

# Lab Agent Key (Demo Seed)
# Public Key matches Registry: WjNnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jndz==
LAB_KEY_SEED = b"lab_agent_secret_seed_32_bytes__"
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(LAB_KEY_SEED)

def validate_diagnostic_data(data):
    """
    Validates Observation or DiagnosticReport FHIR resources.
    """
    fhir_bundle = data.get("fhir_bundle")
    if not fhir_bundle or fhir_bundle.get("resourceType") != "Bundle":
        return False, "Invalid or missing FHIR Bundle"
    
    entries = fhir_bundle.get("entry", [])
    resources = [e.get("resource", {}).get("resourceType") for e in entries]
    
    if "Observation" not in resources and "DiagnosticReport" not in resources:
        return False, "Bundle must contain an Observation or DiagnosticReport resource"
    
    return True, "Diagnostic Data Validation Passed"

@functions_framework.http
def lab_agent(request):
    request_json = request.get_json(silent=True)
    if not request_json:
        return "Invalid Request", 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    if method == "attest_diagnostic":
        # 1. Structural Validation
        is_valid, error = validate_diagnostic_data(params)
        if not is_valid:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32001, "message": f"Lab Validation Error: {error}"},
                "id": request_id
            }), 400, {'Content-Type': 'application/json'}

        attestation_id = str(uuid.uuid4())
        
        # 2. Issue Verifiable Credential
        issuance_date = datetime.utcnow().isoformat() + "Z"
        vc_id = f"urn:uuid:{attestation_id}"
        
        credential = {
            "@context": [
                "https://www.w3.org/2018/credentials/v1",
                "https://schema.org/healthcare"
            ],
            "id": vc_id,
            "type": ["VerifiableCredential", "DiagnosticAttestationCredential"],
            "issuer": "did:web:lab-v1.gov",
            "issuanceDate": issuance_date,
            "credentialSubject": {
                "id": params.get("provider_did", "unknown"),
                "diagnosticType": params.get("diagnostic_type", "LabResult"),
                "status": "Verified",
                "policyMatched": params.get("policy_id", "standard-lab-v1")
            }
        }

        # 3. Cryptographic Signature
        credential_bytes = json.dumps(credential).encode('utf-8')
        signature = private_key.sign(credential_bytes)
        
        credential["proof"] = {
            "type": "Ed25519Signature2020",
            "created": issuance_date,
            "verificationMethod": "did:web:lab-v1.gov#key-1",
            "proofPurpose": "assertionMethod",
            "jws": base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        }

        # 4. Audit Trail
        if db:
            db.collection("attestations").document(attestation_id).set({
                "type": "LAB_DIAGNOSTIC",
                "provider_id": params.get("provider_id"),
                "timestamp": firestore.SERVER_TIMESTAMP,
                "status": "Verified"
            })

        return json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "status": "Verified",
                "attestation_id": attestation_id,
                "verifiable_credential": credential
            },
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}

    return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id}), 404
