import json
import boto3
import uuid
import os

# Initialize Bedrock Runtime
bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

def lambda_handler(event, context):
    """
    Voice Agent: Processes natural language voice commands (simulated via text)
    to facilitate healthcare attestations and authorizations.
    """
    body = event.get('body', '{}')
    if isinstance(body, str):
        body = json.loads(body)
    
    method = body.get('method')
    params = body.get('params', {})
    request_id = body.get('id', str(uuid.uuid4()))

    if method == "process_voice_command":
        user_input = params.get("text", "")
        
        # Use Bedrock (Claude 3.5 Sonnet) to interpret the command
        try:
            prompt = f"System: You are an AI Voice Agent for a healthcare attestation network. \
                     Interpret the following user request and provide a professional, concise response. \
                     User Request: {user_input}"
            
            response = bedrock.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 512,
                    "messages": [{"role": "user", "content": prompt}]
                })
            )
            
            response_body = json.loads(response.get('body').read())
            ai_interpretation = response_body['content'][0]['text']
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "jsonrpc": "2.0",
                    "result": {
                        "voice_response": ai_interpretation,
                        "intent": "VOICE_PROCESSED",
                        "status": "SUCCESS"
                    },
                    "id": request_id
                })
            }
        except Exception as e:
            # Fallback to mock response if Bedrock call fails (e.g. in local/mock mode)
            print(f"Bedrock call failed: {e}")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "jsonrpc": "2.0",
                    "result": {
                        "voice_response": f"I've received your request: '{user_input}'. I am processing this with the necessary clinical agents.",
                        "intent": "VOICE_PROCESSED",
                        "status": "MOCK_SUCCESS"
                    },
                    "id": request_id
                })
            }

    return {
        'statusCode': 404,
        'body': json.dumps({
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": request_id
        })
    }
