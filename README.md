# CMS A2A Attestation Network

A production-grade, multi-cloud (AWS/GCP) agentic framework for autonomous healthcare attestation and prior-authorization validation.

## 📖 Detailed Documentation

- **[Project Overview](docs/OVERVIEW.md)**: Mission, components, and multi-cloud strategy.
- **[Architecture & Design](docs/ARCHITECTURE.md)**: Technical data flow, security model, and trust registry.
- **[API Reference](docs/API_REFERENCE.md)**: JSON-RPC methods and data formats.
- **[Setup & Testing](docs/SETUP.md)**: Local installation and cloud deployment guide.

## 🧩 The 10-Agent Ecosystem

This project implements a decentralized healthcare mesh using the **Agent-to-Agent (A2A)** pattern:

1.  **Provider Agent**: Initiates medical necessity attestations.
2.  **Clearinghouse Agent**: The central nexus for verification and orchestration.
3.  **CMS Agent**: Government oversight and policy enforcement.
4.  **Payer Agent**: Automated prior authorization and claims.
5.  **PBM Agent**: Pharmacy benefit and medication validation.
6.  **Lab Agent**: Diagnostic and clinical evidence attestations.
7.  **Auditor Agent**: Real-time regulatory audit of the ecosystem.
8.  **Credentialing Agent**: Provider license (NPI) and trust verification.
9.  **Patient Agent**: Patient data ownership and consent management.
10. **Research Agent**: AI-driven clinical trial matching using verified data.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Terraform
- GCP & AWS accounts (or LocalStack/Local Mock mode)

### Installation

```bash
pip install -r requirements.txt
```

### Running the Full Ecosystem Demo

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 scripts/test_phase10_ecosystem.py
```

### Simple Usage Example

You can also run a simple, standalone request:

```bash
python3 scripts/example_usage.py
```

## 🔐 Security Features

- **W3C Verifiable Credentials**: Standardized attestation formats.
- **Ed25519 Cryptography**: Real digital signatures for non-repudiation and integrity.
- **Trust Registry**: Decentralized identity (DID) resolution for automated verification.
- **Multi-Cloud Handshake**: Secure AWS-GCP cross-cloud verification.

## 🛠 Tech Stack

- **GCP**: Cloud Functions, Firestore, Vertex AI (Gemini 1.5 Flash).
- **AWS**: Lambda, DynamoDB, S3, Bedrock (Claude 3.5 Sonnet).
- **Security**: Ed25519 (Cryptography), JSON-RPC 2.0.
- **IaC**: Terraform (HCL).

---

_Developed for CMS A2A Innovation_
