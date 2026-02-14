# CMS A2A Multi-Agent Deployment Architecture - README

## 🚀 Overview

This project implements an enterprise-grade, production-ready deployment architecture for the CMS A2A (Agent-to-Agent) Attestation Network with:

- **Shadow Deployment**: Safe, gradual rollout with automated traffic shifting and rollback
- **Model Armors**: Bedrock Guardrails for PII protection, content filtering, and rate limiting
- **Quality Assurance**: Comprehensive validation framework for model outputs
- **Security Best Practices**: HIPAA compliance, DDoS protection, audit logging
- **Multi-Cloud Support**: AWS and GCP with feature parity

## 📋 Architecture Components

### 1. Shadow Deployment Infrastructure

- **Lambda Aliases**: `production` and `shadow` aliases for each agent
- **Traffic Shifting**: CodeDeploy-managed gradual rollout (10% → 100%)
- **Automated Monitoring**: CloudWatch metrics comparison (errors, duration, throttles)
- **Auto-Rollback**: Automatic rollback on threshold violations
- **State Management**: DynamoDB table tracking deployment state

### 2. Model Armors (Bedrock Guardrails)

- **PII Detection & Redaction**: Healthcare-specific patterns (MBI, NPI, HICN, SSN)
- **Content Filtering**: Hate speech, violence, sexual content, misconduct
- **Topic Policies**: Block medical advice and financial fraud
- **Rate Limiting**: DDoS protection with contextual grounding
- **Audit Logging**: DynamoDB table with 90-day retention

### 3. Quality Assurance Framework

- **Schema Validation**: JSON structure and type checking
- **Hallucination Detection**: Identify overconfident or unsupported claims
- **Completeness Checks**: Ensure responses address all prompt requirements
- **HIPAA Compliance**: Validate required disclaimers and PII redaction
- **Consistency & Accuracy**: Compare against reference data
- **Performance Benchmarking**: Track duration, token count, success rate

### 4. CI/CD Pipeline

- **Security Scanning**: Checkov (IaC) + Bandit (Python)
- **Unit Tests**: Pytest with coverage reporting
- **Lambda Packaging**: Automated ZIP creation for all 11 agents
- **Terraform Deployment**: Automated infrastructure provisioning
- **Shadow Deployment**: Automated traffic shifting with monitoring
- **Integration Tests**: End-to-end validation

## 🛠️ Quick Start

### Prerequisites

- AWS Account with appropriate permissions
- Terraform >= 1.6.0
- Python 3.11+
- AWS CLI configured

### 1. Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan \
  -var="cloud_provider=aws" \
  -var="enable_shadow_deployment=true" \
  -var="enable_bedrock_guardrails=true"

# Apply
terraform apply \
  -var="cloud_provider=aws" \
  -var="enable_shadow_deployment=true" \
  -var="enable_bedrock_guardrails=true" \
  -auto-approve
```

### 2. Execute Shadow Deployment

```bash
# Deploy all agents with 10% traffic split
python scripts/deploy_shadow.py \
  --agent all \
  --traffic-split 10 \
  --monitoring-duration 15

# Deploy specific agent with auto-promotion
python scripts/deploy_shadow.py \
  --agent provider \
  --traffic-split 20 \
  --monitoring-duration 10 \
  --auto-promote

# Rollback deployment
python scripts/deploy_shadow.py \
  --agent provider \
  --rollback

# Promote shadow to production
python scripts/deploy_shadow.py \
  --agent provider \
  --promote
```

### 3. Test Guardrails

```python
from shared.guardrails import safe_bedrock_invoke

# Invoke Bedrock with automatic PII protection
response = safe_bedrock_invoke(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    prompt="Process this claim for patient John Doe, SSN 123-45-6789",
    request_id="test-123"
)

# PII will be automatically redacted/anonymized
```

### 4. Validate Model Output

```python
from shared.qa_framework import QualityAssuranceValidator

qa = QualityAssuranceValidator()

result = qa.validate_output(
    prompt="Validate this prior authorization",
    response=model_response,
    expected_schema={"status": str, "reason": str}
)

if not result.passed:
    print(f"QA failed: {result.failures}")
```

## 📊 Cost Estimates

### AWS Deployment (Optimized)

- **Bedrock Claude 3.5 Sonnet**: $600/month
- **Lambda (11 agents)**: $61/month
- **Bedrock Guardrails**: $300/month
- **DynamoDB**: $25/month
- **CloudWatch**: $20/month
- **CodeDeploy**: $0 (free)
- **X-Ray**: $5/month
- **Total**: **$933/month**

### GCP Deployment (Optimized)

- **Vertex AI Gemini 1.5 Pro**: $219/month
- **Cloud Run (11 agents)**: $45/month
- **Vertex AI Safety Filters**: $15/month
- **Firestore**: $18/month
- **Cloud Monitoring**: $12/month
- **Cloud Trace**: $3/month
- **Total**: **$331/month**

**Cost Savings**: GCP is **65% cheaper** than AWS ($331 vs $933/month)

## 🔒 Security Features

### HIPAA Compliance

- ✅ PII detection and redaction (SSN, MBI, NPI, HICN)
- ✅ Encryption at rest (DynamoDB, S3)
- ✅ Encryption in transit (TLS 1.2+)
- ✅ Audit logging (90-day retention)
- ✅ Access controls (IAM roles, least privilege)

### DDoS Protection

- ✅ Rate limiting via Bedrock Guardrails
- ✅ CloudWatch alarms for anomalous traffic
- ✅ Automated throttling and backoff

### Content Security

- ✅ Input/output filtering
- ✅ Profanity blocking
- ✅ Topic policies (medical advice, fraud)
- ✅ Contextual grounding (hallucination prevention)

## 📈 Monitoring & Observability

### CloudWatch Metrics

- `RequestDuration`: Lambda execution time
- `RequestSuccess`: Success/failure rate
- `GuardrailBlocked`: PII detections and violations
- `ShadowErrorRate`: Shadow vs production error comparison
- `ShadowDurationAnomaly`: Performance degradation detection

### Alarms

- High PII detection rate (>50 per 5 minutes)
- Rate limit exceeded (>100 per minute)
- Shadow error rate increase (>5%)
- Shadow duration increase (>50%)

### Audit Logs

- **Deployment State**: DynamoDB table tracking all deployments
- **Guardrail Violations**: DynamoDB table with violation details
- **Attestation Ledger**: DynamoDB table with all attestation results

## 🧪 Testing

### Unit Tests

```bash
pytest tests/ -v --cov=aws_lambda --cov=shared
```

### Integration Tests

```bash
pytest tests/test_phase10_ecosystem.py -v
```

### Guardrail Validation

```bash
python -c "
import boto3
bedrock = boto3.client('bedrock-runtime')
response = bedrock.apply_guardrail(
    guardrailIdentifier='your-guardrail-id',
    guardrailVersion='1',
    source='INPUT',
    content=[{'text': {'text': 'My SSN is 123-45-6789'}}]
)
assert response['action'] == 'GUARDRAIL_INTERVENED'
print('✅ Guardrails working correctly')
"
```

## 🚦 CI/CD Workflow

### Automated Deployment

```bash
# Trigger via GitHub Actions
git push origin main

# Or manual trigger with custom parameters
gh workflow run deploy.yml \
  -f environment=production \
  -f traffic_split=10 \
  -f auto_promote=false
```

### Pipeline Stages

1. **Security Scan**: Checkov + Bandit
2. **Unit Tests**: Pytest with coverage
3. **Build**: Lambda package creation
4. **Terraform Plan**: Infrastructure preview
5. **Deploy Infrastructure**: Terraform apply
6. **Shadow Deployment**: Automated traffic shifting
7. **Integration Tests**: End-to-end validation
8. **Notify**: Failure notifications

## 📚 Documentation

- [Implementation Plan](docs/implementation_plan.md)
- [Cost Estimate](docs/cost_estimate.md)
- [Architecture Diagram](generated-diagrams/cms_a2a_multicloud_architecture.png)
- [API Reference](docs/API_REFERENCE.md)
- [Technical Guide](docs/TECHNICAL_GUIDE.md)

## 🤝 Contributing

1. Create feature branch
2. Implement changes with tests
3. Run security scans and tests locally
4. Submit PR with detailed description
5. CI/CD pipeline will validate changes

## 📄 License

[Add your license here]

## 🆘 Support

For issues or questions:

- GitHub Issues: [Create an issue]
- Documentation: See `docs/` directory
- Architecture Questions: Review implementation plan
