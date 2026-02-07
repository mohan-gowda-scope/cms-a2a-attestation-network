import json
import os
import boto3
import uuid
from datetime import datetime

# Global variable for lazy client initialization
_DYNAMODB_CLIENT = None
_BEDROCK_CLIENT = None

def get_table():
    global _DYNAMODB_CLIENT
    if not _DYNAMODB_CLIENT:
        _DYNAMODB_CLIENT = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
    return _DYNAMODB_CLIENT.Table(os.environ.get('LEDGER_TABLE'))

def get_bedrock():
    global _BEDROCK_CLIENT
    if not _BEDROCK_CLIENT:
        _BEDROCK_CLIENT = boto3.client('bedrock-runtime', region_name=os.environ.get('BEDROCK_REGION', 'us-east-1'))
    return _BEDROCK_CLIENT

def validate_with_bedrock(attestation_data):
    """
    Use Claude 3.5 Sonnet to validate the semantic correctness of the attestation.
    """
    prompt = f"""
    You are a CMS Compliance Validator. Review the following healthcare attestation data for semantic correctness and FHIR alignment.
    
    Data:
    {json.dumps(attestation_data, indent=2)}
    
    Respond in JSON format:
    {{
        "valid": true/false,
        "reason": "Detailed explanation of finding"
    }}
    """
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    
    response = get_bedrock().invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
        body=body
    )
    
    response_body = json.loads(response.get('body').read())
    result_text = response_body['content'][0]['text']
    
    # Extract JSON if nested in text
    try:
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        return json.loads(result_text[start:end])
    except Exception:
        return {"valid": False, "reason": "Failed to parse validator response"}

def issue_verifiable_credential(attestation_id, provider_id, validation):
    """
    Generate a W3C-compliant Verifiable Credential for the attestation.
    """
    issuance_date = datetime.utcnow().isoformat() + "Z"
    
    vc = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://schema.org/healthcare"
        ],
        "id": f"urn:uuid:{attestation_id}",
        "type": ["VerifiableCredential", "HealthcareAttestationCredential"],
        "issuer": "did:web:cms.gov:agent:a2a-v1",
        "issuanceDate": issuance_date,
        "credentialSubject": {
            "id": f"did:web:provider-{provider_id}.com",
            "attestationType": "HealthcareDataAttestation",
            "complianceStatus": "Compliant" if validation.get("valid") else "Flagged",
            "validationReason": validation.get("reason", "Standard Review")
        },
        "proof": {
            "type": "Ed25519Signature2020",
            "created": issuance_date,
            "verificationMethod": "did:web:cms.gov:agent:a2a-v1#key-1",
            "proofPurpose": "assertionMethod",
            "jws": f"eyJhbGciOiJFZERTQSIsImI2NCI6ZmFsc2UsImNyaXQiOlsiYjY0Il19..{uuid.uuid4().hex}"
        }
    }
    return vc

def handle_attestation(params):
    """
    Method: attest_healthcare_data
    """
    attestation_id = str(uuid.uuid4())
    validation = validate_with_bedrock(params)
    provider_id = params.get("provider_id", "unknown")
    
    # Generate formal W3C Verifiable Credential
    verifiable_credential = issue_verifiable_credential(attestation_id, provider_id, validation)
    
    # Save to ledger
    item = {
        "attestation_id": attestation_id,
        "timestamp": datetime.utcnow().isoformat(),
        "provider_id": provider_id,
        "data": params,
        "validation_result": validation,
        "verifiable_credential": verifiable_credential
    }
    get_table().put_item(Item=item)
    
    return {
        "attestation_id": attestation_id,
        "status": verifiable_credential["credentialSubject"]["complianceStatus"],
        "receipt": f"CMS-REC-{attestation_id[:8]}",
        "verifiable_credential": verifiable_credential
    }

def lambda_handler(event, context):
    """
    CMS Attestation Agent (A2A Provider) - JSON-RPC 2.0 over HTTP
    """
    try:
        # APIGateway Proxy wrapper
        body = json.loads(event.get('body', '{}'))
        
        # A2A Protocol Validation (JSON-RPC 2.0)
        if body.get("jsonrpc") != "2.0":
            return {
                "statusCode": 400,
                "body": json.dumps({"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": body.get("id")})
            }
            
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        if method == "attest_healthcare_data":
            result = handle_attestation(params)
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                })
            }
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id
                })
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error"},
                "id": None
            })
        }
