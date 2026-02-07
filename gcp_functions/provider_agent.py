import functions_framework
import json
import os
import urllib.request
import uuid

def request_prior_auth(provider_id, patient_id, cms_vc):
    """
    Initiate an A2A Prior Auth request to a Payer.
    """
    ch_endpoint = os.environ.get('CLEARINGHOUSE_A2A_ENDPOINT')
    payload = {
        "jsonrpc": "2.0",
        "method": "request_prior_auth",
        "params": {
            "provider_id": provider_id,
            "patient_id": patient_id,
            "verifiable_credential": cms_vc,
            "clinical_data": {
                "cpt_code": "99213",
                "diagnosis": "Z00.00"
            }
        },
        "id": str(uuid.uuid4())
    }
    
    req = urllib.request.Request(
        ch_endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

@functions_framework.http
def provider_agent(request):
    """
    Healthcare Provider Agent - Phase 3 Logic
    """
    # Simulate a trigger (e.g., file upload result)
    # 1. First get Attestation (Phase 1/2) 
    # 2. Then use result to get Prior Auth (Phase 3)
    
    # For this demo, we'll assume a CMS VC is already available
    mock_cms_vc = {
        "id": "urn:uuid:mock-vc-123",
        "issuer": "did:web:cms.gov:agent:a2a-v1",
        "proof": {"type": "Ed25519Signature2020", "verificationMethod": "did:web:cms.gov:agent:a2a-v1#key-1"}
    }
    
    auth_result = request_prior_auth("GCP-PROV-99", "PAT-555", mock_cms_vc)
    
    return json.dumps({
        "flow": "Prior-Auth-Pipeline",
        "payer_response": auth_result
    }), 200, {'Content-Type': 'application/json'}
