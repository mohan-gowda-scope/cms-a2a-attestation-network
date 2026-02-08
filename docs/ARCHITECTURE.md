# Architecture & Design

## System Architecture

The CMS A2A Network follows a decentralized, event-driven architecture. Agents operate autonomously within their own cloud environments, communicating via standard protocols.

### Data Flow (The "Attestation Handshake")

1.  **Ingestion**: A provider drops a FHIR bundle (claims/clinical data) into an S3 bucket or triggers a GCF.
2.  **Request**: The Provider Agent constructs a `JSON-RPC` request: `attest_healthcare_data`.
3.  **Proxying**: The Clearinghouse receives the request, logs the `tenant_id` and `timestamp` to Firestore, and forwards it to the CMS Agent.
4.  **Semantic Validation**: The CMS Agent uses Gemini 1.5 Flash to analyze the FHIR bundle for compliance and data quality.
5.  **Issuance**:
    - CMS Agent generates a Verifiable Credential (VC).
    - The VC is signed using the CMS **Ed25519** Private Key.
    - The signature covers the `id` and `issuanceDate`.
6.  **Verification**: The Provider Agent receives the VC and initiates a `request_prior_auth` with the Payer Agent.
7.  **Auto-Approval**: The Payer Agent resolves the CMS DID in the `TrustRegistry`, verifies the signature, and auto-generates an Authorization ID if the proof is valid.

## Component Breakdown

### Cloud Infrastructure (IaC)

- **Terraform (AWS)**: Provisions Lambda functions, S3 buckets, and IAM roles.
- **Terraform (GCP)**: Provisions Cloud Functions, Firestore collections, and Vertex AI endpoints.

### Security Implementation

- **Cryptographic Library**: `cryptography` (Python) for Ed25519.
- **Signature Type**: `Ed25519Signature2020`.
- **Proof Format**: JWS (JSON Web Signature) detached content format.

## Error Handling & Robustness

The system implements robust error handling for:

- **Network Interruptions**: Retries for JSON-RPC calls.
- **Invalid Proofs**: Granular denial reasons in Payer responses.
- **Environment Parity**: Logic is characterized to run in local mock mode (for development) or production cloud mode (for deployment).
