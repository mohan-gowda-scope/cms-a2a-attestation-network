# Technical Guide: Multi-Cloud A2A Attestation

This document details the technical implementation of the Agent-to-Agent communication and the choice-based infrastructure of the CMS Attestation Network.

## 1. Decentralized Identity (DID)

Every agent in the network has a unique `did:web` identifier. We achieve **Cloud-Agnostic Identity** by using standardized Ed25519 keys that are independent of cloud provider-specific IAM.

### Identity Lifecycle

1. **Registry**: Agents are listed in the [Trust Registry](file:///Users/mohangowda/projects/cms-a2a-attestation/shared/trust_registry.py).
2. **Resolution**: Requesting agents resolve the target DID to an endpoint (Lambda URL or Cloud Run URL).
3. **Handshake**: Payloads are signed using the agent's private key and verified by the receiver.

## 2. Infrastructure Choice (Terraform)

The architecture is modular. Use the `cloud_provider` variable in `terraform/variables.tf` to toggle between stacks.

### AWS Independent Stack

- **Entrypoint**: API Gateway
- **Compute**: 10 Independent Lambda Functions (Python 3.11)
- **AI**: Amazon Bedrock (Anthropic Claude 3.5 Sonnet)
- **Persistence**: DynamoDB Global Tables

### GCP Independent Stack

- **Entrypoint**: Cloud Run Load Balancer
- **Compute**: 10 Independent Cloud Run Services
- **AI**: Google Vertex AI (Gemini 1.5 Flash)
- **Persistence**: Firestore (Native Mode)

## 3. The JSON-RPC 2.0 Interface

All agents, regardless of cloud, speak a standardized JSON-RPC 2.0 protocol.

```json
{
  "jsonrpc": "2.0",
  "method": "request_attestation",
  "params": {
    "patient_id": "PAT-1234",
    "provider_id": "did:web:mayo.com",
    "clinical_data": { "FHIR": "..." }
  },
  "id": "transaction-001"
}
```

## 4. Local Simulation & Demo Mode

The `one_click_demo.py` script manages the complexities of cross-cloud testing by:

- Injecting mock environments for agents when running in non-cloud environments.
- Handling the different response formats of AWS Lambda (proxy responses) vs GCP Cloud Functions.
- Validating the 10-agent lifecycle flow across the chosen provider.
