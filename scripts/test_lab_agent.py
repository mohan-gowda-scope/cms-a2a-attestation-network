import json
from gcp_functions.lab_agent import lab_agent

class MockRequest:
    def __init__(self, data):
        self.data = data
    def get_json(self, silent=True):
        return self.data

def test_lab_attestation():
    print("--- CMS A2A Network: Lab Agent Test ---")
    
    # 1. Prepare Diagnostic Bundle (HbA1c Result)
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
            },
            {
                "fullUrl": "Observation/OBS-001",
                "resource": {
                    "resourceType": "Observation",
                    "id": "OBS-001",
                    "status": "final",
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "4548-4", "display": "Hemoglobin A1c/Hemoglobin.total in Blood"}]
                    },
                    "subject": {"reference": "Patient/123"},
                    "valueQuantity": {
                        "value": 7.2,
                        "unit": "%",
                        "system": "http://unitsofmeasure.org",
                        "code": "%"
                    }
                }
            }
        ]
    }

    # 2. Request Lab Attestation
    request_data = {
        "jsonrpc": "2.0",
        "method": "attest_diagnostic",
        "params": {
            "provider_id": "PROV-EXAMPLE-1",
            "provider_did": "did:web:provider-PROV-EXAMPLE-1.com",
            "policy_id": "lab_policy_v1",
            "diagnostic_type": "HbA1c_Lab",
            "fhir_bundle": fhir_bundle
        },
        "id": "lab-test-001"
    }

    print(f"\n[Provider] Sending diagnostic attestation for lab: HbA1c (Result: 7.2%)")
    
    req = MockRequest(request_data)
    response_raw, status_code, headers = lab_agent(req)
    
    response = json.loads(response_raw)
    
    if "result" in response:
        result = response["result"]
        print(f"\n[Lab] Response Received!")
        print(f"Status: {result['status']}")
        
        vc = result["verifiable_credential"]
        print(f"\n[Lab] Verifiable Credential Issued:")
        print(json.dumps(vc, indent=2))
    else:
        print(f"\n[Error] Lab Agent returned: {response.get('error')}")

if __name__ == "__main__":
    test_lab_attestation()
