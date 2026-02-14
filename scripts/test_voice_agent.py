import json
import sys
import os

# Add local path to sys.path to import local agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from aws_lambda.voice_agent import lambda_handler

def test_voice_agent_flow():
    print("=== CMS A2A Network: Voice Agent Integration Test ===")
    
    # 1. Test Voice Command: Requesting Authorization status
    print("\n[Step 1] Voice Command: 'Check status of my prior auth for patient-123'")
    mock_event = {
        "body": json.dumps({
            "jsonrpc": "2.0",
            "method": "process_voice_command",
            "params": {"text": "Check status of my prior auth for patient-123"},
            "id": "voice-test-001"
        })
    }
    
    response = lambda_handler(mock_event, None)
    resp_body = json.loads(response['body'])
    
    if "result" in resp_body:
        result = resp_body["result"]
        print(f"Voice Response: {result['voice_response']}")
        print(f"Status: {result['status']}")
        print(f"Intent: {result['intent']}")

    # 2. Test Voice Command: Triggering a new request (Example)
    print("\n[Step 2] Voice Command: 'Start a new lab attestation for HbA1c test'")
    mock_event_2 = {
        "body": json.dumps({
            "jsonrpc": "2.0",
            "method": "process_voice_command",
            "params": {"text": "Start a new lab attestation for HbA1c test"},
            "id": "voice-test-002"
        })
    }
    
    response_2 = lambda_handler(mock_event_2, None)
    resp_body_2 = json.loads(response_2['body'])
    
    if "result" in resp_body_2:
        result_2 = resp_body_2["result"]
        print(f"Voice Response: {result_2['voice_response']}")
        print(f"Status: {result_2['status']}")

if __name__ == "__main__":
    test_voice_agent_flow()
