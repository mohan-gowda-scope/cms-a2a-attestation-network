import json

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "agent": "Patient",
                "status": "Active (AWS Stack)",
                "data": "A2A Trust Protocol Operational"
            },
            "id": 1
        })
    }
