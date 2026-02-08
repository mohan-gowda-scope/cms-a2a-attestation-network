# Setup & Testing Guide

## Local Development Setup

### 1. Prerequisites

- Python 3.10+
- `pip`

### 2. Install Dependencies

```bash
pip install -r gcp_functions/requirements.txt
```

### 3. Run E2E Orchestration Simulation

The orchestration script simulates the full multi-agent flow locally without requiring cloud credentials.

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 scripts/e2e_orchestrator.py
```

### 4. Simple Usage Example

For a minimal example of a provider requesting an attestation from CMS:

```bash
python3 scripts/example_usage.py
```

## Cloud Deployment (IaC)

### GCP Deployment

1.  Navigate to `terraform_gcp/`.
2.  Initialize and Apply:
    ```bash
    terraform init
    terraform apply
    ```
3.  Ensure the environment variable `GCP_PROJECT` is set in the Cloud Function configuration.

### AWS Deployment

1.  Navigate to `terraform/`.
2.  Initialize and Apply:
    ```bash
    terraform init
    terraform apply
    ```

## Verification & Testing

### Unit Tests

Run the project test suite:

```bash
pytest tests/
```

### Security Scanning

As per global rules, we use **Checkov** to scan infrastructure for security vulnerabilities:

```bash
checkov -d terraform/
checkov -d terraform_gcp/
```
