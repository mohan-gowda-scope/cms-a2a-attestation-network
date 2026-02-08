import base64

class TrustRegistry:
    """
    Mock Decentralized Trust Registry.
    Resolves DIDs to Public Keys and Service Endpoints.
    """
    REGISTRY = {
        "did:web:cms.gov:agent:a2a-v1": {
            "public_key": "d3Nnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jn=", # cms_agent
            "endpoint": "https://us-central1-cms-project.cloudfunctions.net/cms_agent",
            "type": "CMSAttestationAgent"
        },
        "did:web:provider-PROV-EXAMPLE-1.com": {
            "public_key": "YXJnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jndw==", # provider
            "endpoint": "https://api.provider-example.com/a2a/attest",
            "type": "HealthcareProvider"
        },
        "did:web:payer-AETNA-1.com": {
            "public_key": "YXJnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jndw==", 
            "endpoint": "https://api.payer-example.com/v1/auth",
            "type": "HealthInsurer"
        },
        "did:web:pbm-v1.gov": {
            "public_key": "Yndyd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jndz==", 
            "endpoint": "https://us-central1-pbm-project.cloudfunctions.net/pbm_agent",
            "type": "PharmacyBenefitManager"
        },
        "did:web:lab-v1.gov": {
            "public_key": "WjNnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jndz==", 
            "endpoint": "https://us-central1-lab-project.cloudfunctions.net/lab_agent",
            "type": "DiagnosticLab"
        },
        "did:web:auditor-v1.gov": {
            "public_key": "QXVkaXRvcl9QdWJsaWNfS2V5X1BsYWNlaG9sZGVyXzMyQg==", 
            "endpoint": "https://us-central1-auditor-project.cloudfunctions.net/auditor_agent",
            "type": "RegulatoryAuditor"
        },
        "did:web:credentialing-v1.gov": {
            "public_key": "Q3JlZGVudGlhbGluZ19QdWJsaWNfS2V5X1BsYWNlaG9sZA==", 
            "endpoint": "https://us-central1-cred-project.cloudfunctions.net/credentialing_agent",
            "type": "CredentialingBody"
        },
        "did:web:patient-v1.me": {
            "public_key": "UGF0aWVudF9QdWJsaWNfS2V5X1BsYWNlaG9sZGVyXzMxQg==", 
            "endpoint": "https://patient-proxy.healthcare.me/agent",
            "type": "PatientProxy"
        },
        "did:web:research-v1.edu": {
            "public_key": "UmVzZWFyY2hfUHVibGljX0tleV9QbGFjZWhvbGRlcl8zMg==", 
            "endpoint": "https://us-central1-research-project.cloudfunctions.net/research_agent",
            "type": "ClinicalResearchBody"
        }
    }

    @classmethod
    def resolve_did(cls, did: str):
        """
        Mimics a DID resolver. Returns the document (metadata) for a given DID.
        """
        return cls.REGISTRY.get(did)

    @classmethod
    def get_public_key(cls, did: str):
        """
        Extracts and decodes the public key for an agent.
        """
        registry_entry = cls.resolve_did(did)
        if registry_entry:
            return base64.b64decode(registry_entry["public_key"])
        return None
