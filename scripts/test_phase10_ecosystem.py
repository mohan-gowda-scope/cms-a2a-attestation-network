import json
from gcp_functions.patient_agent import patient_agent
from gcp_functions.research_agent import research_agent

class MockRequest:
    def __init__(self, data):
        self.data = data
    def get_json(self, silent=True):
        return self.data

def test_patient_research_flow():
    print("=== CMS A2A Network: Phase 10 Patient & Research Test ===")
    
    # 1. Mock a Diagnostic VC (from Phase 8)
    diagnostic_vc = {
        "type": ["VerifiableCredential", "DiagnosticAttestationCredential"],
        "issuer": "did:web:lab-v1.gov",
        "credentialSubject": {
            "id": "did:web:patient-123.me",
            "diagnosticType": "HbA1c_Lab",
            "status": "Verified",
            "value": 7.2
        }
    }

    # 2. Test Patient Agent (Store VC)
    print("\n[Step 1] Patient Proxy: Storing Diagnostic VC and verifying consent")
    patient_req = MockRequest({
        "jsonrpc": "2.0",
        "method": "store_credential",
        "params": {"verifiable_credential": diagnostic_vc},
        "id": "patient-test-001"
    })
    resp_raw, _, _ = patient_agent(patient_req)
    resp = json.loads(resp_raw)
    if "result" in resp:
        print("VC Successfully encrypted and stored in Patient Vault.")

    # 3. Test Research Agent (Trial Match)
    print("\n[Step 2] Clinical Research: Evaluating eligibility for 'Diabetes Type-2 Study'")
    research_req = MockRequest({
        "jsonrpc": "2.0",
        "method": "evaluate_trial_eligibility",
        "params": {
            "trial_criteria": "Adults with HbA1c > 7.0%",
            "verified_credentials": [diagnostic_vc]
        },
        "id": "research-test-001"
    })
    resp_raw, status_code, headers = research_agent(research_req)
    resp = json.loads(resp_raw)
    
    if "result" in resp:
        match = resp["result"]["match_result"]
        print(f"Match Result: {'Eligible' if match['eligible'] else 'Ineligible'} (Confidence: {match['confidence']})")
        print(f"Reasoning: {match['reasoning']}")

if __name__ == "__main__":
    test_patient_research_flow()
