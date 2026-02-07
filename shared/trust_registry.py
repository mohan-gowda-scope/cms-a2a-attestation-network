import json

class TrustRegistry:
    """
    Simulated Trust Registry for A2A Healthcare Network.
    Enables agents to resolve DIDs (Decentralized Identifiers) to Public Keys.
    """
    
    TRUSTED_ISSUERS = {
        "did:web:cms.gov:agent:a2a-v1": {
            "publicKey": "z6MkpTHR8VNsBxYbmSGF9C78zB4B8P4tC18mP3kP9p9p9", # Mock Ed25519 Key
            "name": "Centers for Medicare & Medicaid Services (CMS)",
            "roles": ["Issuer"],
            "verificationMethod": "did:web:cms.gov:agent:a2a-v1#key-1"
        },
        "did:web:clearinghouse.io:agent": {
            "publicKey": "z6MkgT9p9p9pVNsBxYbmSGF9C78zB4B8P4tC18mP3kP",
            "name": "Secure Healthcare Clearinghouse Hub",
            "roles": ["Verifier", "Proxy"],
            "verificationMethod": "did:web:clearinghouse.io:agent#key-1"
        }
    }

    @classmethod
    def resolve_issuer(cls, did):
        """
        Resolve a DID to its metadata and public key.
        """
        return cls.TRUSTED_ISSUERS.get(did, None)

    @classmethod
    def verify_proof(cls, verifiable_credential):
        """
        Simulated verification of a VC proof.
        Checks if the issuer is in the trust registry and validates the proof block.
        """
        issuer_did = verifiable_credential.get("issuer")
        issuer_info = cls.resolve_issuer(issuer_did)
        
        if not issuer_info:
            return False, "Issuer not found in Trust Registry"
            
        proof = verifiable_credential.get("proof", {})
        if proof.get("verificationMethod") != issuer_info.get("verificationMethod"):
            return False, "Invalid verification method for issuer"
            
        # In production, this would use ed25519.verify(key, signature, message)
        return True, "Credential Verified via Trust Registry"

if __name__ == "__main__":
    # Internal test of Resolve logic
    cms_info = TrustRegistry.resolve_issuer("did:web:cms.gov:agent:a2a-v1")
    print(f"Resolved Trusted Issuer: {cms_info['name']}")
