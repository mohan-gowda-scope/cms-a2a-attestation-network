import json
import uuid
import time
from shared.trust_registry import TrustRegistry
# Mocking the functions for local orchestration
from gcp_functions.cms_agent import cms_agent
from gcp_functions.clearinghouse_agent import clearinghouse_agent
from gcp_functions.payer_agent import payer_agent

class MockRequest:
    def __init__(self, data):
        self.data = data
    def get_json(self, silent=True):
        return self.data

def run_e2e_flow():
    print("=== CMS A2A Attestation Network: E2E Orchestration Simulation ===\n")
    provider_id = "GCP-PROV-99"
    patient_id = "PAT-555"
    
    # Step 1: Provider triggers Attestation via Clearinghouse
    print(f"[Provider] Requesting attestation for {provider_id}...")
    attestation_request = {
        "jsonrpc": "2.0",
        "method": "attest_healthcare_data",
        "params": {
            "provider_id": provider_id,
            "patient_id": patient_id,
            "fhir_bundle": {"resourceType": "Bundle", "entry": []}
        },
        "id": "req-1"
    }
    
    # Simulate Clearinghouse proxying to CMS
    # We'll mock the internal forward_to_cms in clearinghouse_agent.py
    # or just call cms_agent directly for this simulation
    print("[Clearinghouse] Proxying request to CMS Agent...")
    cms_req = MockRequest(attestation_request)
    # Note: In a real flow, this would be an HTTP call. 
    # Here we mock the result of cms_agent
    
    # CMS Validation & Signing
    print("[CMS] Validating data with Vertex AI and signing Verifiable Credential...")
    # Mocking environmental variables for firestore/aiplatform if needed, 
    # but assuming code can run or be mocked.
    try:
        cms_response_raw, status_code, headers = cms_agent(cms_req)
        cms_result = json.loads(cms_response_raw)
        vc = cms_result["result"]["verifiable_credential"]
        print(f"[CMS] Issued VC: {vc['id']} (Status: {cms_result['result']['status']})")
    except Exception as e:
        print(f"[ERROR] CMS Agent failed: {e}")
        return

    # Step 2: Clearinghouse verifies the VC before returning to Provider
    print("[Clearinghouse] Verifying VC signature...")
    is_valid, msg = TrustRegistry.verify_proof(vc)
    print(f"[Clearinghouse] Verification result: {is_valid} - {msg}")

    # Step 3: Provider uses VC to request Prior Auth from Payer
    print("\n[Provider] Using CMS VC to request Prior Authorization from Payer Agent...")
    prior_auth_request = {
        "jsonrpc": "2.0",
        "method": "request_prior_auth",
        "params": {
            "provider_id": provider_id,
            "patient_id": patient_id,
            "verifiable_credential": vc,
            "clinical_data": {"cpt_code": "99213"}
        },
        "id": "req-2"
    }
    
    payer_req = MockRequest(prior_auth_request)
    payer_response_raw, status_code, headers = payer_agent(payer_req)
    payer_result = json.loads(payer_response_raw)
    
    print(f"[Payer] Response: {payer_result['result']['status']} (Auth ID: {payer_result['result'].get('auth_id')})")
    print(f"[Payer] Notes: {payer_result['result'].get('notes')}")

    print("\n=== E2E Flow Completed Successfully ===")

if __name__ == "__main__":
    run_e2e_flow()
