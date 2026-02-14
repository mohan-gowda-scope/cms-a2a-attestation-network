"""
Bedrock Guardrails Integration for CMS A2A Agents

This module provides helper functions to integrate Bedrock Guardrails
into agent Lambda functions for PII protection, content filtering,
and rate limiting.

Usage:
    from shared.guardrails import apply_guardrails, log_violation
    
    # Apply guardrails to user input
    safe_input = apply_guardrails(
        content=user_input,
        guardrail_id="abc123",
        guardrail_version="1",
        source="INPUT"
    )
    
    # Apply guardrails to model output
    safe_output = apply_guardrails(
        content=model_response,
        guardrail_id="abc123",
        guardrail_version="1",
        source="OUTPUT"
    )
"""

import boto3
import json
import os
import time
from typing import Dict, Optional, Literal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# AWS Clients
bedrock_runtime = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

# Configuration from environment
PROJECT_NAME = os.environ.get('PROJECT_NAME', 'cms-a2a-attestation')
AUDIT_LOG_TABLE = f"{PROJECT_NAME}-guardrail-audit-log"


class GuardrailViolation(Exception):
    """Raised when content violates guardrail policies"""
    def __init__(self, message: str, violation_type: str, details: Dict):
        super().__init__(message)
        self.violation_type = violation_type
        self.details = details


def apply_guardrails(
    content: str,
    guardrail_id: str,
    guardrail_version: str,
    source: Literal["INPUT", "OUTPUT"] = "INPUT",
    request_id: Optional[str] = None
) -> str:
    """
    Apply Bedrock Guardrails to content
    
    Args:
        content: Text content to check
        guardrail_id: Bedrock Guardrail ID
        guardrail_version: Guardrail version
        source: Whether this is INPUT or OUTPUT content
        request_id: Optional request ID for audit logging
    
    Returns:
        Sanitized content (with PII anonymized if applicable)
    
    Raises:
        GuardrailViolation: If content violates guardrail policies
    """
    try:
        logger.info(f"Applying guardrails to {source} content (length: {len(content)})")
        
        response = bedrock_runtime.apply_guardrail(
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version,
            source=source,
            content=[
                {
                    'text': {
                        'text': content
                    }
                }
            ]
        )
        
        action = response.get('action')
        
        if action == 'GUARDRAIL_INTERVENED':
            # Content was blocked or modified
            assessments = response.get('assessments', [])
            outputs = response.get('outputs', [])
            
            # Check if content was completely blocked
            if not outputs:
                violation_details = {
                    'action': action,
                    'assessments': assessments,
                    'source': source,
                    'content_length': len(content)
                }
                
                # Log violation
                if request_id:
                    log_violation(
                        request_id=request_id,
                        violation_type='CONTENT_BLOCKED',
                        details=violation_details
                    )
                
                raise GuardrailViolation(
                    message="Content blocked by guardrails",
                    violation_type='CONTENT_BLOCKED',
                    details=violation_details
                )
            
            # Content was modified (e.g., PII anonymized)
            sanitized_content = outputs[0]['text']
            
            logger.info(f"Content modified by guardrails: {len(content)} → {len(sanitized_content)} chars")
            
            # Log PII detections
            if request_id:
                pii_detections = [
                    a for a in assessments 
                    if a.get('sensitiveInformationPolicy')
                ]
                if pii_detections:
                    log_violation(
                        request_id=request_id,
                        violation_type='PII_DETECTED',
                        details={
                            'pii_count': len(pii_detections),
                            'pii_types': [
                                entity.get('type') 
                                for a in pii_detections 
                                for entity in a.get('sensitiveInformationPolicy', {}).get('piiEntities', [])
                            ]
                        }
                    )
            
            return sanitized_content
        
        # No intervention needed
        return content
        
    except bedrock_runtime.exceptions.ThrottlingException:
        logger.error("Bedrock Guardrails rate limit exceeded")
        if request_id:
            log_violation(
                request_id=request_id,
                violation_type='RATE_LIMIT_EXCEEDED',
                details={'source': source}
            )
        raise GuardrailViolation(
            message="Rate limit exceeded",
            violation_type='RATE_LIMIT_EXCEEDED',
            details={'source': source}
        )
    
    except Exception as e:
        logger.error(f"Error applying guardrails: {e}")
        raise


def log_violation(
    request_id: str,
    violation_type: str,
    details: Dict
) -> None:
    """
    Log guardrail violation to DynamoDB audit table
    
    Args:
        request_id: Unique request identifier
        violation_type: Type of violation (CONTENT_BLOCKED, PII_DETECTED, etc.)
        details: Additional violation details
    """
    try:
        table = dynamodb.Table(AUDIT_LOG_TABLE)
        
        timestamp = int(time.time())
        ttl = timestamp + (90 * 24 * 60 * 60)  # 90 days
        
        table.put_item(
            Item={
                'request_id': request_id,
                'timestamp': timestamp,
                'violation_type': violation_type,
                'details': json.dumps(details),
                'ttl': ttl,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Logged {violation_type} violation for request {request_id}")
        
    except Exception as e:
        logger.error(f"Error logging violation: {e}")


def get_guardrail_config() -> Dict[str, str]:
    """
    Get guardrail configuration from environment variables
    
    Returns:
        Dict with guardrail_id and guardrail_version
    """
    return {
        'pii_guardrail_id': os.environ.get('PII_GUARDRAIL_ID'),
        'pii_guardrail_version': os.environ.get('PII_GUARDRAIL_VERSION', 'DRAFT'),
        'rate_limit_guardrail_id': os.environ.get('RATE_LIMIT_GUARDRAIL_ID'),
        'rate_limit_guardrail_version': os.environ.get('RATE_LIMIT_GUARDRAIL_VERSION', 'DRAFT')
    }


def safe_bedrock_invoke(
    model_id: str,
    prompt: str,
    guardrail_config: Optional[Dict] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> str:
    """
    Invoke Bedrock model with guardrails applied to both input and output
    
    Args:
        model_id: Bedrock model ID
        prompt: User prompt
        guardrail_config: Guardrail configuration (optional)
        request_id: Request ID for audit logging
        **kwargs: Additional arguments for invoke_model
    
    Returns:
        Model response with guardrails applied
    """
    config = guardrail_config or get_guardrail_config()
    
    # Apply guardrails to input
    if config.get('pii_guardrail_id'):
        safe_prompt = apply_guardrails(
            content=prompt,
            guardrail_id=config['pii_guardrail_id'],
            guardrail_version=config['pii_guardrail_version'],
            source="INPUT",
            request_id=request_id
        )
    else:
        safe_prompt = prompt
    
    # Invoke model
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": kwargs.get('max_tokens', 4096),
        "messages": [
            {
                "role": "user",
                "content": safe_prompt
            }
        ],
        "temperature": kwargs.get('temperature', 0.7)
    })
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    model_output = response_body['content'][0]['text']
    
    # Apply guardrails to output
    if config.get('pii_guardrail_id'):
        safe_output = apply_guardrails(
            content=model_output,
            guardrail_id=config['pii_guardrail_id'],
            guardrail_version=config['pii_guardrail_version'],
            source="OUTPUT",
            request_id=request_id
        )
    else:
        safe_output = model_output
    
    return safe_output
