import json
from gcp_functions.auditor_agent import auditor_agent
from gcp_functions.credentialing_agent import credentialing_agent

class MockRequest:
    def __init__(self, data):
        self.data = data
    def get_json(self, silent=True):
        return self.data

def test_governance_flow():
    print("=== CMS A2A Network: Phase 9 Governance Test ===")
    
    # 1. Test Credentialing Agent (NPI Verification)
    print("\n[Step 1] Verifying Practitioner License (NPI: 1234567890)")
    cred_req = MockRequest({
        "jsonrpc": "2.0",
        "method": "verify_practitioner",
        "params": {
            "npi": "1234567890",
            "practitioner_did": "did:web:practitioner-123.com",
            "specialization": "Orthopedic Surgery"
        },
        "id": "cred-test-001"
    })
    resp_raw, status_code, _ = credentialing_agent(cred_req)
    resp = json.loads(resp_raw)
    
    if "result" in resp:
        print("Professional Credential Issued Successfully.")
    else:
        print(f"Credentialing Error: {resp.get('error')}")

    # 2. Test Auditor Agent (Audit Report)
    print("\n[Step 2] Performing Regulatory Audit Scan")
    audit_req = MockRequest({
        "jsonrpc": "2.0",
        "method": "perform_audit",
        "params": {"period": "last_24h"},
        "id": "audit-test-001"
    })
    resp_raw, status_code, _ = auditor_agent(audit_req)
    resp = json.loads(resp_raw)
    
    if "result" in resp:
        print("Audit Report Generated Successfully.")
        print(f"Summary: {resp['result']['audit_report']['credentialSubject']['auditResults']}")
    else:
        print(f"Audit Error: {resp.get('error')}")

if __name__ == "__main__":
    test_governance_flow()
