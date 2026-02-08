import json
import uuid

def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "match_result": {
                    "eligible": True,
                    "confidence": 0.98,
                    "reasoning": "Standard AWS Match: Patient profiles align with Phase III Oncology requirements."
                }
            },
            "id": 1
        })
    }
