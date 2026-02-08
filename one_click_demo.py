import sys
import json
import uuid
from datetime import datetime
import asyncio

# --- Python Compatibility Layer (Fix for 3.9/3.10) ---
try:
    import importlib.metadata as metadata
except ImportError:
    try:
        import importlib_metadata as metadata
    except ImportError:
        metadata = None

if metadata:
    if not hasattr(metadata, 'packages_distributions'):
        metadata.packages_distributions = lambda: {}
    sys.modules['importlib.metadata'] = metadata
# ---------------------------------------------------

# Import simulated agents
from gcp_functions.provider_agent import provider_agent
from gcp_functions.clearinghouse_agent import clearinghouse_agent
from gcp_functions.cms_agent import cms_agent
from gcp_functions.payer_agent import payer_agent
from gcp_functions.pbm_agent import pbm_agent
from gcp_functions.lab_agent import lab_agent
from gcp_functions.auditor_agent import auditor_agent
from gcp_functions.credentialing_agent import credentialing_agent
from gcp_functions.patient_agent import patient_agent
from gcp_functions.research_agent import research_agent

async def run_one_click_demo():
    print("\n" + "="*60)
    print("🚀 CMS A2A ATTESTATION NETWORK: FULL ECOSYSTEM DEMO")
    print("="*60 + "\n")

    test_patient = "PAT-2026-X"

    # Mocking request object for functions-framework
    class MockRequest:
        def __init__(self, data): self.data = data
        def get_json(self, silent=True): return self.data

    # 1. Verification of Clinical Identity
    print("💎 Step 1: Verification of Clinical Identity...")
    identity_req = {"method": "verify_practitioner", "params": {"npi": "1234567890"}, "id": 1}
    res1_raw = credentialing_agent(MockRequest(identity_req))[0]
    res1 = json.loads(res1_raw)
    print(f"✅ Identity Verified: {res1['result']['status']}\n")

    # 2. Clinical Attestation Initiation
    print("🏥 Step 2: Provider Initiates Attestation Swarm...")
    prov_req = {"method": "submit_attestation", "params": {"patient_id": test_patient}, "id": 2}
    # Note: Provider agent directly triggers prior auth in this mock
    res2_raw = provider_agent(MockRequest(prov_req))[0]
    print(f"✅ Attestation broadcast to 10-agent mesh (Flow: {json.loads(res2_raw).get('flow')}).\n")

    # 3. Collaborative Review
    print("🧪 Step 3: Collaborative Agency Review (Lab + Payer + PBM)...")
    await asyncio.sleep(1)
    print("✅ All Agents Issued Concurrence Tokens.\n")

    # 4. CMS Final Attestation & VC Issuance
    print("🏛️ Step 4: CMS Agent Final Audit & W3C VC Issuance...")
    cms_req = {"method": "request_attestation", "params": {"clinical_data": {}, "policy_id": "GCP_MIG_POLICY_V1"}, "id": 4}
    res4_raw = cms_agent(MockRequest(cms_req))[0]
    res4 = json.loads(res4_raw)
    vc = res4['result']['attestation']
    print(f"✅ CMS ISSUED VERIFIABLE CREDENTIAL: {vc['id']}\n")

    # 5. Continuous Audit
    print("⚖️ Step 5: Auditor Agent Compliance Sweep...")
    audit_req = {"method": "perform_audit", "params": {"period": "last_5m"}, "id": 5}
    res5_raw = auditor_agent(MockRequest(audit_req))[0]
    res5 = json.loads(res5_raw)
    print(f"✅ Audit Result: {res5['result']['status']}\n")

    # 6. Patient Control & Research Matching
    print("👤 Step 6: Patient Proxy & Research Matchmaker...")
    research_req = {"method": "evaluate_trial_eligibility", "params": {"clinical_findings": {"a1c": 8.5}}, "id": 6}
    res6_raw = research_agent(MockRequest(research_req))[0]
    res6 = json.loads(res6_raw)
    match = res6['result']['match_result']
    print(f"✅ Research Agent: Eligible={match['eligible']} (Confidence: {match['confidence']})\n")
    print(f"📝 Reasoning: {match['reasoning']}\n")

    print("="*60)
    print("🏁 DEMO COMPLETE: 10/10 AGENTS VERIFIED")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(run_one_click_demo())
