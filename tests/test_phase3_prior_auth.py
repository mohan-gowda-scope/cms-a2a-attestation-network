import json
import os
import sys
from unittest.mock import MagicMock, patch

# Add relevant directories to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lambda')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared')))

from clearinghouse_agent import lambda_handler as ch_handler
from payer_agent import lambda_handler as payer_handler

def test_phase3_prior_auth_flow():
    """
    Test Phase 3: Provider -> Clearinghouse -> Payer (VC Verified)
    """
    print("Starting Phase 3: Autonomous Prior Authorization E2E Test...")
    
    # 1. Setup Mock VC (received from CMS in earlier phase)
    mock_cms_vc = {
        "id": "urn:uuid:cms-vc-999",
        "type": ["VerifiableCredential", "HealthcareAttestationCredential"],
        "issuer": "did:web:cms.gov:agent:a2a-v1",
        "proof": {
            "type": "Ed25519Signature2020",
            "verificationMethod": "did:web:cms.gov:agent:a2a-v1#key-1"
        }
    }
    
    # 2. Provider Payload for Prior Auth
    prior_auth_payload = {
        "jsonrpc": "2.0",
        "method": "request_prior_auth",
        "params": {
            "provider_id": "AWS-PROV-123",
            "patient_id": "PAT-ABC",
            "verifiable_credential": mock_cms_vc,
            "clinical_data": {"cpt": "99213"}
        },
        "id": "p3-test-1"
    }
    
    event = {"body": json.dumps(prior_auth_payload)}
    
    # 3. Mocks for Clearinghouse and Payer Handshake
    with patch('urllib.request.urlopen') as mock_urlopen, \
         patch('boto3.resource') as mock_db, \
         patch('trust_registry.TrustRegistry.verify_proof') as mock_vc_verify:
        
        # Setup DB Mocks
        mock_table = MagicMock()
        mock_db.return_value.Table.return_value = mock_table
        
        # Mock Trust Registry Verification (Called by Payer)
        mock_vc_verify.return_value = (True, "Trust Hub: Credential Verified")
        
        # 4. Mock the Payer Agent Endpoint (Called by Clearinghouse)
        mock_payer_res = MagicMock()
        mock_payer_res.read.return_value = json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "prior_auth_id": "AUTH-XYZ123",
                "status": "Auto-Approved",
                "valid_until": "2027-02-07"
            },
            "id": "p3-test-1"
        }).encode('utf-8')
        mock_payer_res.__enter__.return_value = mock_payer_res
        mock_urlopen.return_value = mock_payer_res
        
        # Execute Clearinghouse Agent
        os.environ['PAYER_A2A_ENDPOINT'] = 'https://mock-payer/auth'
        os.environ['LEDGER_TABLE'] = 'mock-ledger'
        
        print("-> Clearinghouse Proxying request to Payer...")
        response = ch_handler(event, None)
        
        # 5. Assertions
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        result = body.get("result", {})
        
        print(f"-> Payer Response Status: {result.get('status')}")
        assert result.get('status') == "Auto-Approved"
        assert "prior_auth_id" in result
        
        print("PASS: Phase 3 Prior Auth Flow Verified Successfully!")

if __name__ == "__main__":
    test_phase3_prior_auth_flow()
