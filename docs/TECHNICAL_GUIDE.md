# Technical Guide: A2A Handshake & Attestation

This document details the technical implementation of the Agent-to-Agent communication used in the CMS Attestation Network.

## 1. Decentralized Identity (DID)

Every agent in the network has a unique `did:web` identifier registered in the [Trust Registry](file:///Users/mohangowda/projects/cms-a2a-attestation/shared/trust_registry.py).

### Identity Resolution Flow

1. **Lookup**: An agent looks up the destination DID in the registry.
2. **Key Retrieval**: Retrieves the Public Key (Ed25519) and Endpoint URL.
3. **Verify**: Any received payload must be signed by the corresponding Private Key.

## 2. The JSON-RPC 2.0 Interface

All agents communicate via a standardized JSON-RPC 2.0 interface:

```json
{
  "jsonrpc": "2.0",
  "method": "request_attestation",
  "params": {
    "patient_id": "PAT-1234",
    "provider_id": "did:web:mayo.com",
    "clinical_data": { ... }
  },
  "id": "abc-123"
}
```

## 3. Multi-Cloud Orchestration (Clearinghouse)

The Clearinghouse Agent acts as a bridge between GCP and AWS:

- **Incoming**: Receives JSON-RPC over HTTPS (GCP GCF).
- **Processing**: Orchestrates parallel calls to Lab (GCP) and Payer (AWS).
- **Output**: Returns a bundled multi-signed Verifiable Credential (VC).

## 4. AI-Driven Compliance

The ecosystem uses **Gemini 1.5 Flash** for:

- **Medical Necessity**: Matching patient history to policy documents.
- **Audit**: Scanning the ledger for compliance anomalies.
- **Research**: Matching signed lab results to trial criteria.

## 5. Security Scanning

All Terraform code is scanned using **Checkov** to ensure least-privilege IAM and secure cloud configuration.
