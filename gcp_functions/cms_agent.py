import functions_framework
import json
import os
import uuid
import base64
from datetime import datetime
from google.cloud import firestore
import google.cloud.aiplatform as aiplatform
from vertexai.generative_models import GenerativeModel, Part
from cryptography.hazmat.primitives.asymmetric import ed25519
from shared.trust_registry import TrustRegistry
from shared.privacy_utils import mask_phi
from shared.crypto_utils import sign_credential

# Initialize Clients
try:
    db = firestore.Client()
    aiplatform.init(project=os.environ.get('GCP_PROJECT'), location='us-central1')
    model = GenerativeModel("gemini-1.5-flash-001")
    MOCK_GCP = False
except Exception:
    print("Warning: GCP Clients not initialized. Using mocks for local execution.")
    db = None
    model = None
    MOCK_GCP = True

# CMS Private Key (Seed)
PRIVATE_KEY_SEED = b"secret_seed_for_cms_agent_32_byt" 
private_key = ed25519.Ed25519PrivateKey.from_private_bytes(PRIVATE_KEY_SEED)

def validate_with_vertex_ai(attestation_data, policy_data=None):
    if MOCK_GCP:
        return {"status": "Compliant", "reason": f"Validated against {policy_data.get('policy_id', 'standard')} (Mock)"}

    policy_str = json.dumps(policy_data, indent=2) if policy_data else "Standard Healthcare Guidelines"
    prompt = f"Expert Auditor Role. Validate FHIR Bundle against POLICY: {policy_str}. DATA: {json.dumps(attestation_data)}"
    
    if not model: return {"valid": True, "reason": "Mock"}
    response = model.generate_content(prompt)
    try:
        res = response.text
        start, end = res.find('{'), res.rfind('}') + 1
        return json.loads(res[start:end])
    except: return {"valid": False, "reason": "Parse error"}

def issue_verifiable_credential(attestation_id, tenant_id, validation):
    credential = {
        "@context": ["https://www.w3.org/2018/credentials/v1", "https://schema.org/healthcare"],
        "id": f"urn:uuid:{attestation_id}",
        "type": ["VerifiableCredential", "HealthcareAttestationCredential"],
        "issuer": "did:web:cms.gov:agent:a2a-v1",
        "credentialSubject": {
            "id": f"did:web:provider-{tenant_id}.com",
            "attestationType": "GCPMigrationValidation",
            "complianceStatus": "Compliant" if validation.get("valid") else "Flagged",
            "validationReason": validation.get("reason", "Automated Review")
        }
    }
    return sign_credential(credential, private_key, "did:web:cms.gov:agent:a2a-v1#key-1")

@functions_framework.http
def cms_agent(request):
    request_json = request.get_json(silent=True)
    if not request_json: return "Invalid Request", 400
    
    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    if method == "request_attestation":
        fhir_bundle = params.get("clinical_data")
        policy_id = params.get("policy_id")
        
        # 1. Mask PHI via shared utility
        masked_data = mask_phi(fhir_bundle)
        
        # 2. Semantic Analysis
        validation = validate_with_vertex_ai(masked_data, {"policy_id": policy_id})
        
        # 3. Issue Signed VC via shared utility
        attestation_id = str(uuid.uuid4())
        vc = issue_verifiable_credential(attestation_id, params.get("tenant_id", "demo"), validation)
        
        # 4. Persistence
        if db:
            db.collection("attestations").document(attestation_id).set({
                "vc": vc, "timestamp": datetime.utcnow().isoformat(), "policy": policy_id
            })

        return json.dumps({"jsonrpc": "2.0", "result": {"vc_id": vc["id"], "attestation": vc}, "id": request_id}), 200
        
    return "Not Found", 404
