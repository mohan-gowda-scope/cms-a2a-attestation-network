import json
import os
import boto3
import uuid
from datetime import datetime
from trust_registry import TrustRegistry

def get_table():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(os.environ.get('AUTH_TABLE'))

def handle_prior_auth(params):
    """
    Method: request_prior_auth
    Logic: Autonomously approves if a valid CMS-issued VC is presented.
    """
    vc = params.get("verifiable_credential")
    if not vc:
        return {"status": "Denied", "reason": "No Verifiable Credential presented"}
    
    # Verify the CMS VC using the Trust Registry
    is_valid, msg = TrustRegistry.verify_proof(vc)
    if not is_valid:
        return {"status": "Denied", "reason": f"Untrusted Credential: {msg}"}
    
    # Instant Decision Logic (Simplified)
    # In production, this would check clinical criteria (CPT codes, etc.)
    prior_auth_id = f"AUTH-{uuid.uuid4().hex[:8].upper()}"
    
    # Save to Payer Auth Ledger
    item = {
        "auth_id": prior_auth_id,
        "timestamp": datetime.utcnow().isoformat(),
        "provider_id": params.get("provider_id"),
        "patient_id": params.get("patient_id"),
        "status": "Auto-Approved",
        "vc_ref": vc.get("id")
    }
    get_table().put_item(Item=item)
    
    return {
        "prior_auth_id": prior_auth_id,
        "status": "Auto-Approved",
        "valid_until": (datetime.now().replace(year=datetime.now().year + 1)).isoformat()
    }

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")

        if method == "request_prior_auth":
            result = handle_prior_auth(params)
            return {
                "statusCode": 200,
                "body": json.dumps({"jsonrpc": "2.0", "result": result, "id": request_id})
            }
        
        return {"statusCode": 404, "body": json.dumps({"error": "Method not found"})}
            
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
