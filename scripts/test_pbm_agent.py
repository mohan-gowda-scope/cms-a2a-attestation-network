import json
from gcp_functions.pbm_agent import pbm_agent

class MockRequest:
    def __init__(self, data):
        self.data = data
    def get_json(self, silent=True):
        return self.data

def test_pbm_attestation():
    print("--- CMS A2A Network: PBM Agent Test ---")
    
    # 1. Prepare Medication Bundle
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
                "fullUrl": "MedicationRequest/M-001",
                "resource": {
                    "resourceType": "MedicationRequest",
                    "id": "M-001",
                    "status": "active",
                    "intent": "order",
                    "medicationCodeableConcept": {
                        "coding": [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": "866386", "display": "Adalimumab 40 MG/0.8 ML"}]
                    },
                    "subject": {"reference": "Patient/123"}
                }
            }
        ]
    }

    # 2. Request PBM Attestation
    request_data = {
        "jsonrpc": "2.0",
        "method": "attest_medication",
        "params": {
            "provider_id": "PROV-EXAMPLE-1",
            "provider_did": "did:web:provider-PROV-EXAMPLE-1.com",
            "policy_id": "pbm_policy_v1",
            "medication_code": "866386",
            "fhir_bundle": fhir_bundle
        },
        "id": "pbm-test-001"
    }

    print(f"\n[Provider] Sending medication attestation for drug: Humira (866386)")
    
    req = MockRequest(request_data)
    response_raw, status_code, headers = pbm_agent(req)
    
    response = json.loads(response_raw)
    
    if "result" in response:
        result = response["result"]
        print(f"\n[PBM] Response Received!")
        print(f"Status: {result['status']}")
        
        vc = result["verifiable_credential"]
        print(f"\n[PBM] Verifiable Credential Issued:")
        print(json.dumps(vc, indent=2))
    else:
        print(f"\n[Error] PBM Agent returned: {response.get('error')}")

if __name__ == "__main__":
    test_pbm_attestation()
