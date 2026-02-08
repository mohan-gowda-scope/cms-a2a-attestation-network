import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import ed25519

def sign_credential(credential, private_key, verification_method):
    """
    Signs a W3C Verifiable Credential using Ed25519.
    Adds the 'proof' section to the dictionary.
    """
    issuance_date = datetime.utcnow().isoformat() + "Z"
    if "issuanceDate" not in credential:
        credential["issuanceDate"] = issuance_date
        
    credential_bytes = json.dumps(credential).encode('utf-8')
    signature = private_key.sign(credential_bytes)
    
    credential["proof"] = {
        "type": "Ed25519Signature2020",
        "created": issuance_date,
        "verificationMethod": verification_method,
        "proofPurpose": "assertionMethod",
        "jws": base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    }
    return credential

def verify_credential(credential, public_key_bytes):
    """
    Verifies the Ed25519 signature of a W3C Verifiable Credential.
    """
    try:
        proof = credential.get("proof", {})
        if not proof:
            return False
            
        # Copy and remove proof for verification
        cred_copy = credential.copy()
        del cred_copy["proof"]
        jws = proof.get("jws")
        
        signature = base64.urlsafe_b64decode(jws + '=' * (4 - len(jws) % 4))
        public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
        
        cred_bytes = json.dumps(cred_copy).encode('utf-8')
        public_key.verify(signature, cred_bytes)
        return True
    except Exception as e:
        print(f"Verification failing: {e}")
        return False
