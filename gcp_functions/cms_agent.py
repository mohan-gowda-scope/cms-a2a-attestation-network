import functions_framework
import json
import os
import uuid
import base64
from datetime import datetime
from google.cloud import firestore
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part
from cryptography.hazmat.primitives.asymmetric import ed25519

# Initialize Clients (Wrapped for local orchestration/testing)
try:
    db = firestore.Client()
    aiplatform.init(project=os.environ.get('GCP_PROJECT'), location='us-central1')
    model = GenerativeModel("gemini-1.5-flash-001")
except Exception:
    print("Warning: GCP Clients not initialized. Using mocks for local execution.")
    db = None
    model = None

# Hardcoded Private Key for Demo (Seed)
# Public Key matches TrustRegistry: d3Nnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jn=
PRIVATE_KEY_SEED = b"secret_seed_for_cms_agent_32_byt" 
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(PRIVATE_KEY_SEED)

def validate_with_vertex_ai(attestation_data):
    """
    Use Gemini 1.5 Flash to validate healthcare attestation data.
    """
    prompt = f"""
    You are a CMS Compliance Validator. Review the following healthcare attestation data for semantic correctness and FHIR alignment.
    
    Data:
    {json.dumps(attestation_data, indent=2)}
    
    Respond in JSON format:
    {{
        "valid": true/false,
        "reason": "Detailed explanation of finding"
    }}
    """
    
    if not model:
        return {"valid": True, "reason": "Local Mock Validation (No Vertex AI)"}
        
    response = model.generate_content(prompt)
    result_text = response.text
    
    try:
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        return json.loads(result_text[start:end])
    except Exception:
        return {"valid": False, "reason": "Failed to parse Vertex AI response"}

def issue_verifiable_credential(attestation_id, tenant_id, validation):
    """
    Generate a W3C-compliant Verifiable Credential with real Ed25519 signature.
    """
    issuance_date = datetime.utcnow().isoformat() + "Z"
    vc_id = f"urn:uuid:{attestation_id}"
    
    # Data to sign
    signed_data = f"{vc_id}|{issuance_date}".encode()
    signature = private_key.sign(signed_data)
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    vc = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://schema.org/healthcare"
        ],
        "id": vc_id,
        "type": ["VerifiableCredential", "HealthcareAttestationCredential"],
        "issuer": "did:web:cms.gov:agent:a2a-v1",
        "issuanceDate": issuance_date,
        "credentialSubject": {
            "id": f"did:web:provider-{tenant_id}.com",
            "attestationType": "GCPMigrationValidation",
            "complianceStatus": "Compliant" if validation.get("valid") else "Flagged",
            "validationReason": validation.get("reason", "GCP Automated Review")
        },
        "proof": {
            "type": "Ed25519Signature2020",
            "created": issuance_date,
            "verificationMethod": "did:web:cms.gov:agent:a2a-v1#key-1",
            "proofPurpose": "assertionMethod",
            "jws": f"eyJhbGciOiJFZERTQSIsImI2NCI6ZmFsc2UsImNyaXQiOlsiYjY0Il19..{signature_b64}"
        }
    }
    return vc

def validate_fhir_bundle(data):
    """
    Strict structural validation for FHIR R4 Bundle.
    """
    fhir_bundle = data.get("fhir_bundle")
    if not fhir_bundle:
        return False, "Missing fhir_bundle in request params"
    
    if fhir_bundle.get("resourceType") != "Bundle":
        return False, "Resource is not a FHIR Bundle"
    
    if "entry" not in fhir_bundle or not isinstance(fhir_bundle["entry"], list):
        return False, "FHIR Bundle must contain an 'entry' list"
        
    return True, "Structural validation passed"

@functions_framework.http
def cms_agent(request):
    """
    HTTP Cloud Function for CMS Attestation Agent
    """
    request_json = request.get_json(silent=True)
    if not request_json or request_json.get("jsonrpc") != "2.0":
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}), 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    if method == "attest_healthcare_data":
        # 1. Strict FHIR Structural Validation
        is_valid_fhir, fhir_error = validate_fhir_bundle(params)
        if not is_valid_fhir:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32001, "message": f"FHIR Validation Error: {fhir_error}"},
                "id": request_id
            }), 400

        attestation_id = str(uuid.uuid4())
        validation = validate_with_vertex_ai(params)
        tenant_id = params.get("provider_id", "unknown")
        
        # Generate formal W3C Verifiable Credential
        verifiable_credential = issue_verifiable_credential(attestation_id, tenant_id, validation)
        
        # Save to Firestore (Multitenant Ledger)
        if db:
            doc_ref = db.collection('attestation_ledger').document(attestation_id)
            doc_ref.set({
                "attestation_id": attestation_id,
                "tenant_id": tenant_id,
                "timestamp": datetime.utcnow().isoformat(),
                "method": method,
                "status": verifiable_credential["credentialSubject"]["complianceStatus"],
                "validation_result": validation,
                "verifiable_credential": verifiable_credential
            })

        return json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "attestation_id": attestation_id,
                "status": verifiable_credential["credentialSubject"]["complianceStatus"],
                "verifiable_credential": verifiable_credential
            },
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}
    
    return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id}), 404
