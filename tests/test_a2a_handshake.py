import json
import os
from unittest.mock import MagicMock, patch
import sys

# Add lambda and shared directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lambda')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'shared')))

from cms_agent import lambda_handler as cms_handler
from clearinghouse_agent import lambda_handler as ch_handler

def test_clearinghouse_a2a_flow():
    """
    Simulate Provider -> Clearinghouse -> CMS flow.
    """
    print("Starting E2E Clearinghouse A2A Flow Test...")
    
    # Set environment variables for testing
    os.environ['AWS_REGION'] = 'us-east-1'
    os.environ['LEDGER_TABLE'] = 'test-table'
    os.environ['CMS_A2A_ENDPOINT'] = 'https://mock-cms/cms'
    
    # Payload from Provider
    provider_payload = {
        "jsonrpc": "2.0",
        "method": "attest_healthcare_data",
        "params": {
            "provider_id": "TENANT-XYZ",
            "attestation_type": "ClinicalQuality",
            "data": {"score": 95}
        },
        "id": "ch-id-001"
    }
    
    event = {"body": json.dumps(provider_payload)}
    
    # Mock Boto3 and Urllib
    with patch('boto3.resource') as mock_dynamodb, \
         patch('urllib.request.urlopen') as mock_urlopen, \
         patch('boto3.client') as mock_bedrock:
        
        # 1. Mock Bedrock (called by CMS Agent)
        mock_bedrock_runtime = MagicMock()
        mock_bedrock.return_value = mock_bedrock_runtime
        mock_stream = MagicMock()
        mock_stream.read.return_value = json.dumps({
            "content": [{"text": '{"valid": true, "reason": "Clearinghouse check passed"}'}]
        }).encode('utf-8')
        mock_bedrock_runtime.invoke_model.return_value = {'body': mock_stream}

        # 2. Mock CMS Agent Response (Handled via urllib in CH Agent)
        mock_cms_res = MagicMock()
        mock_cms_res.read.return_value = json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "status": "Compliant", 
                "attestation_id": "cms-uuid-123",
                "verifiable_credential": {
                    "issuer": "did:web:cms.gov:agent:a2a-v1",
                    "type": ["VerifiableCredential", "HealthcareAttestationCredential"],
                    "proof": {
                        "type": "Ed25519Signature2020",
                        "verificationMethod": "did:web:cms.gov:agent:a2a-v1#key-1"
                    }
                }
            },
            "id": "ch-id-001"
        }).encode('utf-8')
        mock_cms_res.__enter__.return_value = mock_cms_res
        mock_urlopen.return_value = mock_cms_res
        
        # 3. Setup DynamoDB Mock
        mock_table = MagicMock()
        mock_dynamodb.return_value.Table.return_value = mock_table
        
        # 4. Mock TrustRegistry (since it's imported in the handler)
        with patch('trust_registry.TrustRegistry.verify_proof') as mock_verify:
            mock_verify.return_value = (True, "Credential Verified via Trust Registry")
            
            # Execute Clearinghouse Agent
            response = ch_handler(event, None)
            
            # Validate Flow
            print(f"Clearinghouse Status: {response['statusCode']}")
            body = json.loads(response['body'])
            print(f"Final Response: {json.dumps(body, indent=2)}")
            
            assert response['statusCode'] == 200
            assert body['result']['status'] == "Compliant"
            assert "verifiable_credential" in body['result']
            assert body['clearinghouse_verdict'] == "Credential Verified via Trust Registry"
        
        # Verify Clearinghouse logged to DynamoDB
        assert mock_table.put_item.called
        
        print("E2E Clearinghouse Test Passed Successfully!")

if __name__ == "__main__":
    test_clearinghouse_a2a_flow()
