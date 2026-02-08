import functions_framework
import json
import os
from datetime import datetime
import google.cloud.aiplatform as aiplatform
from vertexai.generative_models import GenerativeModel

# Initialize Clients
try:
    aiplatform.init(project=os.environ.get('GCP_PROJECT'), location='us-central1')
    model = GenerativeModel("gemini-1.5-flash-001")
    MOCK_GCP = False
except Exception:
    print("Warning: GCP Research Agent: Clients not initialized. Using mocks.")
    model = None
    MOCK_GCP = True

@functions_framework.http
def research_agent(request):
    """
    Clinical Research Agent: Matches patients to trials using signed attestations.
    """
    request_json = request.get_json(silent=True)
    if not request_json:
        return "Invalid Request", 400

    method = request_json.get("method")
    params = request_json.get("params", {})
    request_id = request_json.get("id")

    if method == "evaluate_trial_eligibility":
        trial_criteria = params.get("trial_criteria", "Adults with HbA1c > 7.0%")
        verified_credentials = params.get("verified_credentials", [])

        # AI-driven Matching Logic
        prompt = f"""
        Evaluate if a patient is eligible for a clinical trial based on these verified credentials.
        
        Trial Criteria: {trial_criteria}
        Verified Credentials: {json.dumps(verified_credentials)}
        
        Return a JSON response:
        {{
            "eligible": true/false,
            "confidence": 0-1.0,
            "reasoning": "brief explanation"
        }}
        """
        
        if model and not MOCK_GCP:
            response = model.generate_content(prompt)
            match_result = json.loads(response.text.replace('```json', '').replace('```', '').strip())
        else:
            # Mock Matching Result
            match_result = {
                "eligible": True,
                "confidence": 0.95,
                "reasoning": "Patient has attested HbA1c of 7.2%, meeting the >7.0% criterion."
            }

        return json.dumps({
            "jsonrpc": "2.0",
            "result": {
                "match_result": match_result,
                "status": "Evaluation Complete"
            },
            "id": request_id
        }), 200, {'Content-Type': 'application/json'}

    return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": request_id}), 404
