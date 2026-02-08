import os
import json
import uuid
from datetime import datetime

# Centralized Mock Toggle
MOCK_MODE = os.environ.get("DEMO_MODE", "true").lower() == "true"

def get_db_client(provider):
    if MOCK_MODE: return None
    try:
        if provider == "aws":
            import boto3
            return boto3.resource('dynamodb', region_name='us-east-1')
        else:
            from google.cloud import firestore
            return firestore.Client()
    except:
        return None

def sign_attestation(data, private_key):
    # Standard Ed25519 signing for both clouds
    from cryptography.hazmat.primitives.asymmetric import ed25519
    import base64
    
    # Sign
    credential_bytes = json.dumps(data).encode('utf-8')
    signature = private_key.sign(credential_bytes)
    
    data["proof"] = {
        "type": "Ed25519Signature2020",
        "created": datetime.utcnow().isoformat() + "Z",
        "verificationMethod": "did:web:healthcare-trust.gov#key-1",
        "proofPurpose": "assertionMethod",
        "jws": base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    }
    return data
