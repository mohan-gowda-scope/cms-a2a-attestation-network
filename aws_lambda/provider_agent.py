"""
Enhanced Provider Agent with Shadow Deployment, Guardrails, and QA

This agent demonstrates integration of:
1. Shadow deployment support (version tracking)
2. Bedrock Guardrails for PII protection
3. Quality assurance validation
4. Performance monitoring
5. Audit logging
"""

import json
import os
import uuid
import boto3
import time
from datetime import datetime
from typing import Dict, Optional
import sys

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.guardrails import safe_bedrock_invoke, GuardrailViolation, log_violation
from shared.qa_framework import QualityAssuranceValidator, PerformanceBenchmark

# AWS Clients
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

# Configuration
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'cms-a2a-attestation')
LEDGER_TABLE = os.environ.get('LEDGER_TABLE', f'{PROJECT_NAME}-universal-ledger')
AGENT_NAME = 'provider'
AGENT_VERSION = os.environ.get('AWS_LAMBDA_FUNCTION_VERSION', '$LATEST')
DEPLOYMENT_ENV = os.environ.get('DEPLOYMENT_ENV', 'production')

# Initialize QA and Performance tracking
qa_validator = QualityAssuranceValidator(min_passing_score=0.7)
perf_benchmark = PerformanceBenchmark()


def lambda_handler(event, context):
    """
    Enhanced Provider Agent Lambda handler
    
    Handles prior authorization requests with:
    - PII protection via Bedrock Guardrails
    - Quality assurance validation
    - Performance monitoring
    - Audit logging
    """
    request_id = context.request_id if context else str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Log deployment metadata
        log_deployment_metadata(request_id)
        
        # Extract request data
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        operation = body.get('operation', 'attest_healthcare_data')
        patient_data = body.get('patient_data', {})
        
        # Process request based on operation
        if operation == 'attest_healthcare_data':
            result = process_attestation_request(
                patient_data=patient_data,
                request_id=request_id
            )
        else:
            result = {
                'status': 'error',
                'message': f'Unknown operation: {operation}'
            }
        
        # Record performance metrics
        duration_ms = (time.time() - start_time) * 1000
        perf_benchmark.record_benchmark(
            agent_name=AGENT_NAME,
            operation=operation,
            duration_ms=duration_ms,
            token_count=len(json.dumps(result)),
            success=result.get('status') != 'error'
        )
        
        # Publish CloudWatch metrics
        publish_metrics(operation, duration_ms, result.get('status') == 'success')
        
        return {
            'statusCode': 200 if result.get('status') != 'error' else 400,
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-ID': request_id,
                'X-Agent-Version': AGENT_VERSION,
                'X-Deployment-Env': DEPLOYMENT_ENV
            },
            'body': json.dumps(result)
        }
        
    except GuardrailViolation as e:
        # Guardrail blocked the request
        duration_ms = (time.time() - start_time) * 1000
        
        return {
            'statusCode': 403,
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-ID': request_id
            },
            'body': json.dumps({
                'status': 'blocked',
                'message': str(e),
                'violation_type': e.violation_type
            })
        }
        
    except Exception as e:
        # Unexpected error
        duration_ms = (time.time() - start_time) * 1000
        
        perf_benchmark.record_benchmark(
            agent_name=AGENT_NAME,
            operation='error',
            duration_ms=duration_ms,
            token_count=0,
            success=False
        )
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'X-Request-ID': request_id
            },
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }


def process_attestation_request(patient_data: Dict, request_id: str) -> Dict:
    """
    Process healthcare attestation request with guardrails and QA
    
    Args:
        patient_data: Patient and claim data
        request_id: Unique request identifier
    
    Returns:
        Attestation result
    """
    # Build prompt for AI model
    prompt = f"""
    You are a healthcare provider agent validating a prior authorization request.
    
    Patient Data:
    {json.dumps(patient_data, indent=2)}
    
    Please validate this request and provide:
    1. Attestation status (APPROVED, DENIED, PENDING)
    2. Reason for decision
    3. Required documentation (if any)
    4. Next steps
    
    Respond in JSON format with keys: status, reason, required_docs, next_steps
    
    IMPORTANT: Do not provide medical advice. This is for administrative validation only.
    """
    
    # Invoke Bedrock with guardrails
    model_response = safe_bedrock_invoke(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        prompt=prompt,
        request_id=request_id,
        max_tokens=2048,
        temperature=0.3
    )
    
    # Validate response with QA framework
    qa_result = qa_validator.validate_output(
        prompt=prompt,
        response=model_response,
        expected_schema={
            'status': str,
            'reason': str,
            'required_docs': list,
            'next_steps': str
        },
        agent_name=AGENT_NAME
    )
    
    if not qa_result.passed:
        # QA validation failed - log and return error
        log_qa_failure(request_id, qa_result)
        
        return {
            'status': 'error',
            'message': 'Response failed quality assurance checks',
            'qa_score': qa_result.overall_score,
            'qa_failures': [
                {'check': f.check_type.value, 'message': f.message}
                for f in qa_result.failures
            ]
        }
    
    # Parse and return validated response
    try:
        result = json.loads(model_response)
        result['qa_score'] = qa_result.overall_score
        result['request_id'] = request_id
        result['agent_version'] = AGENT_VERSION
        
        # Log to ledger
        log_to_ledger(request_id, result)
        
        return result
        
    except json.JSONDecodeError:
        return {
            'status': 'error',
            'message': 'Invalid response format from AI model',
            'raw_response': model_response[:200]
        }


def log_deployment_metadata(request_id: str) -> None:
    """Log deployment metadata for shadow deployment tracking"""
    try:
        table = dynamodb.Table(f'{PROJECT_NAME}-deployment-state')
        
        table.put_item(
            Item={
                'agent_name': AGENT_NAME,
                'deployment_id': f'{AGENT_NAME}-{AGENT_VERSION}-{int(time.time())}',
                'status': 'ACTIVE',
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': json.dumps({
                    'version': AGENT_VERSION,
                    'environment': DEPLOYMENT_ENV,
                    'request_id': request_id
                })
            }
        )
    except Exception as e:
        print(f"Error logging deployment metadata: {e}")


def log_to_ledger(request_id: str, result: Dict) -> None:
    """Log attestation result to DynamoDB ledger"""
    try:
        table = dynamodb.Table(LEDGER_TABLE)
        
        table.put_item(
            Item={
                'pk': f'ATTESTATION#{request_id}',
                'sk': f'AGENT#{AGENT_NAME}',
                'timestamp': datetime.utcnow().isoformat(),
                'agent_name': AGENT_NAME,
                'agent_version': AGENT_VERSION,
                'result': json.dumps(result),
                'ttl': int(time.time()) + (90 * 24 * 60 * 60)  # 90 days
            }
        )
    except Exception as e:
        print(f"Error logging to ledger: {e}")


def log_qa_failure(request_id: str, qa_result) -> None:
    """Log QA validation failure"""
    try:
        table = dynamodb.Table(f'{PROJECT_NAME}-guardrail-audit-log')
        
        table.put_item(
            Item={
                'request_id': request_id,
                'timestamp': int(time.time()),
                'violation_type': 'QA_VALIDATION_FAILED',
                'details': json.dumps({
                    'agent_name': AGENT_NAME,
                    'qa_score': qa_result.overall_score,
                    'failures': [
                        {'check': f.check_type.value, 'score': f.score, 'message': f.message}
                        for f in qa_result.failures
                    ]
                }),
                'ttl': int(time.time()) + (90 * 24 * 60 * 60)
            }
        )
    except Exception as e:
        print(f"Error logging QA failure: {e}")


def publish_metrics(operation: str, duration_ms: float, success: bool) -> None:
    """Publish custom CloudWatch metrics"""
    try:
        cloudwatch.put_metric_data(
            Namespace=f'{PROJECT_NAME}/Agents',
            MetricData=[
                {
                    'MetricName': 'RequestDuration',
                    'Value': duration_ms,
                    'Unit': 'Milliseconds',
                    'Dimensions': [
                        {'Name': 'AgentName', 'Value': AGENT_NAME},
                        {'Name': 'Operation', 'Value': operation},
                        {'Name': 'Version', 'Value': AGENT_VERSION}
                    ]
                },
                {
                    'MetricName': 'RequestSuccess',
                    'Value': 1 if success else 0,
                    'Unit': 'Count',
                    'Dimensions': [
                        {'Name': 'AgentName', 'Value': AGENT_NAME},
                        {'Name': 'Operation', 'Value': operation},
                        {'Name': 'Version', 'Value': AGENT_VERSION}
                    ]
                }
            ]
        )
    except Exception as e:
        print(f"Error publishing metrics: {e}")
