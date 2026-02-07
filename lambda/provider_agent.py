import json
import os

def lambda_handler(event, context):
    """
    Healthcare Provider Agent (A2A Requester)
    """
    print("Provider Agent triggered")
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Provider Agent Initialized"})
    }
