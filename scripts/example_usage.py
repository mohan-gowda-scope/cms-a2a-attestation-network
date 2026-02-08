import json
from gcp_functions.cms_agent import cms_agent

class MockRequest:
    def __init__(self, data):
        self.data = data
    def get_json(self, silent=True):
        return self.data

def example_request_attestation():
    """
    Demonstrates how to manually call the CMS Agent for healthcare attestation.
    In a production environment, this would be an HTTP POST request to the 
    Cloud Function URL.
    """
    print("--- CMS A2A Network: Simple Usage Example ---")
    
    # 1. Prepare your healthcare data (FHIR Bundle)
    fhir_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "fullUrl": "Patient/123",
                "resource": {
                    "resourceType": "Patient",
                    "id": "123",
                    "name": [{"family": "Doe", "given": ["John"]}]
                }
            }
        ]
    }

    # 2. Construct the JSON-RPC Request
    request_data = {
        "jsonrpc": "2.0",
        "method": "attest_healthcare_data",
        "params": {
            "provider_id": "PROV-EXAMPLE-1",
            "patient_id": "PAT-123",
            "fhir_bundle": fhir_bundle
        },
        "id": "unique-req-id-001"
    }

    print(f"\n[Provider] Sending attestation request for Patient: {request_data['params']['patient_id']}")

    # 3. Call the Agent (Simulated local execution)
    req = MockRequest(request_data)
    response_raw, status_code, headers = cms_agent(req)
    
    # 4. Parse the result and Verifiable Credential
    response = json.loads(response_raw)
    
    if "result" in response:
        result = response["result"]
        print(f"\n[CMS] Response Received!")
        print(f"Status: {result['status']}")
        print(f"Attestation ID: {result['attestation_id']}")
        
        vc = result["verifiable_credential"]
        print(f"\n[CMS] Verifiable Credential Issued:")
        print(json.dumps(vc, indent=2))
    else:
        print(f"\n[Error] Agent returned: {response.get('error')}")

if __name__ == "__main__":
    example_request_attestation()
