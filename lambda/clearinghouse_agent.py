import json
import os
import boto3
import uuid
import urllib.request
from datetime import datetime

# Global variable for lazy client initialization
_DYNAMODB_CLIENT = None

def get_table():
    global _DYNAMODB_CLIENT
    if not _DYNAMODB_CLIENT:
        _DYNAMODB_CLIENT = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    return _DYNAMODB_CLIENT.Table(os.environ.get('LEDGER_TABLE'))

def log_transaction(tenant_id, method, params, status, response):
    """
    Log the A2A transaction into the multitenant Trust Ledger.
    """
    transaction_id = str(uuid.uuid4())
    item = {
        "attestation_id": transaction_id,
        "tenant_id": tenant_id,
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "request_params": params,
        "status": status,
        "cms_response": response
    }
    get_table().put_item(Item=item)
    return transaction_id

def forward_to_cms(payload):
    """
    Forward the A2A request to the Government CMS Agent.
    """
    cms_endpoint = os.environ.get('CMS_A2A_ENDPOINT')
    req = urllib.request.Request(
        cms_endpoint,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read().decode('utf-8'))

def lambda_handler(event, context):
    """
    Clearinghouse Agent (A2A Intermediate) - Multitenant Proxy
    """
    try:
        body = json.loads(event.get('body', '{}'))
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        # Multitenancy check: Extract Provider ID (Tenant)
        tenant_id = params.get("provider_id", "anonymous")
        
        print(f"Clearinghouse processing request for Tenant: {tenant_id}")
        
        # Forwarding Policy: Only certain methods allowed
        if method == "attest_healthcare_data":
            # Call CMS Agent
            cms_response = forward_to_cms(body)
            
            # Phase 2: Verify the Verifiable Credential returned by CMS
            from trust_registry import TrustRegistry # Assumed in path or layer
            vc = cms_response.get("result", {}).get("verifiable_credential")
            is_valid = False
            msg = "No VC provided"
            if vc:
                is_valid, msg = TrustRegistry.verify_proof(vc)
                print(f"Clearinghouse verification: {is_valid} - {msg}")
                cms_response["clearinghouse_verdict"] = msg
                
            # Log as a successful commercial transaction
            log_transaction(tenant_id, method, params, "Verified" if is_valid else "Untrusted", cms_response)
            
            return {
                "statusCode": 200,
                "body": json.dumps(cms_response)
            }
        elif method == "request_prior_auth":
            # Route to Payer Agent
            payer_endpoint = os.environ.get('PAYER_A2A_ENDPOINT')
            req = urllib.request.Request(
                payer_endpoint,
                data=json.dumps(body).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req) as res:
                payer_response = json.loads(res.read().decode('utf-8'))
            
            log_transaction(tenant_id, method, params, "Routed-To-Payer", payer_response)
            
            return {
                "statusCode": 200,
                "body": json.dumps(payer_response)
            }
        else:
            return {
                "statusCode": 403,
                "body": json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method Restricted by Clearinghouse Policy"},
                    "id": request_id
                })
            }
            
    except Exception as e:
        print(f"Clearinghouse Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Clearinghouse Internal Failure"})
        }
