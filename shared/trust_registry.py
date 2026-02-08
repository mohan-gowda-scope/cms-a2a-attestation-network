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
            "public_key": "Yndyd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jnd3Jndz==", # payer
            "endpoint": "https://api.payer-example.com/v1/auth",
            "type": "HealthInsurer"
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
