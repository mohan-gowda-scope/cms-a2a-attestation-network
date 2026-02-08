import functions_framework
import json
import os
import uuid
import urllib.request
from datetime import datetime
from google.cloud import firestore

# Initialize Clients
try:
    db = firestore.Client()
except Exception:
    db = None

def log_transaction(tenant_id, method, params, status, response):
    """
    Log transaction into the GCP Firestore multitenant ledger.
    """
    transaction_id = str(uuid.uuid4())
    if db:
        doc_ref = db.collection('attestation_ledger').document(transaction_id)
        doc_ref.set({
            "attestation_id": transaction_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": method,
            "request_params": params,
            "status": status,
            "cms_response": response
        })
    return transaction_id

from shared.trust_registry import TrustRegistry

def forward_to_cms(payload):
    """
    Forward request to the GCP CMS Agent Cloud Function.
    """
    cms_endpoint = os.environ.get('CMS_A2A_ENDPOINT')
    req = urllib.request.Request(
        cms_endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

def forward_to_payer(payload):
    """
    Forward request to the GCP Payer Agent Cloud Function.
    """
    payer_endpoint = os.environ.get('PAYER_A2A_ENDPOINT')
    req = urllib.request.Request(
        payer_endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

@functions_framework.http
def clearinghouse_agent(request):
    """
    HTTP Cloud Function for Clearinghouse Agent Proxy
    """
    request_json = request.get_json(silent=True)
    if not request_json:
        return {"error": "Invalid Request"}, 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    tenant_id = params.get("provider_id", "anonymous")

    if method == "attest_healthcare_data":
        # Call CMS Cloud Function
        cms_response = forward_to_cms(request_json)
        
        # Phase 2: Verify the Verifiable Credential returned by CMS
        vc = cms_response.get("result", {}).get("verifiable_credential")
        if vc:
            is_valid, msg = TrustRegistry.verify_proof(vc)
            print(f"Clearinghouse verification: {is_valid} - {msg}")
            cms_response["clearinghouse_verdict"] = msg
            
        # Log to Firestore
        log_transaction(tenant_id, method, params, "Verified" if is_valid else "Untrusted", cms_response)
        
        return json.dumps(cms_response), 200, {'Content-Type': 'application/json'}
    
    elif method == "request_prior_auth":
        # Route to Payer Agent
        payer_response = forward_to_payer(request_json)
        
        # Log to Firestore
        log_transaction(tenant_id, method, params, "Routed-To-Payer", payer_response)
        
        return json.dumps(payer_response), 200, {'Content-Type': 'application/json'}
    
    return json.dumps({"error": "Method Restricted"}), 403
