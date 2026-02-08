import json
import base64
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

class TrustRegistry:
    """
    Simulated Trust Registry for A2A Healthcare Network.
    Enables agents to resolve DIDs (Decentralized Identifiers) to Public Keys.
    """
    
    # Hardcoded keys for demonstration purposes (Base64 encoded)
    # CMS Private Key (Seed): secret_seed_for_cms_agent_32_byt
    TRUSTED_ISSUERS = {
        "did:web:cms.gov:agent:a2a-v1": {
            "publicKey": "VJ6zOcffdcAyiKgHyTGifk1SLSREdheAE9Wnu3Jzq6k=", # Valid 32-byte key
            "name": "Centers for Medicare & Medicaid Services (CMS)",
            "roles": ["Issuer"],
            "verificationMethod": "did:web:cms.gov:agent:a2a-v1#key-1"
        },
        "did:web:clearinghouse.io:agent": {
            "publicKey": "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY=",
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
        Verifies an Ed25519 signature in a VC proof block.
        """
        issuer_did = verifiable_credential.get("issuer")
        issuer_info = cls.resolve_issuer(issuer_did)
        
        if not issuer_info:
            return False, "Issuer not found in Trust Registry"
            
        proof = verifiable_credential.get("proof", {})
        if proof.get("type") != "Ed25519Signature2020":
            return False, "Unsupported proof type"

        jws = proof.get("jws", "")
        if ".." not in jws:
            return False, "Invalid JWS format"
        
        # In a real JWS, the signature is the third part, but here we use the second part for simplicity
        _, signature_b64 = jws.split("..")
        
        try:
            public_key_bytes = base64.b64decode(issuer_info["publicKey"])
            signature = base64.urlsafe_b64decode(signature_b64 + "==") # Pad if needed
            
            # Reconstruct the signed data (Header + Payload)
            # For this simplified demo, we sign the VC ID and issuance date
            signed_data = f"{verifiable_credential['id']}|{verifiable_credential['issuanceDate']}".encode()
            
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature, signed_data)
            
            return True, "Credential Verified via Cryptographic Proof"
        except (InvalidSignature, Exception) as e:
            return False, f"Cryptographic Verification Failed: {str(e)}"

if __name__ == "__main__":
    # Internal test logic
    print("Trust Registry Loaded with Ed25519 Support")
