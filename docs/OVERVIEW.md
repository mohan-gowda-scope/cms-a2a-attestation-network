# Project Overview: CMS A2A Attestation Network

## Mission

The CMS A2A (Agent-to-Agent) Attestation Network is a next-generation healthcare data validation system. It enables autonomous, cryptographically secure validation of healthcare attestations between providers, payers, and regulatory bodies (CMS) without manual intervention.

## Key Components

### 1. Provider Agent (AWS / GCP)

Managed by healthcare providers, this agent initiates the attestation flow when new clinical data (FHIR bundles) is received. It orchestrates the process and stores the final approval.

### 2. Clearinghouse Agent (GCP)

Acts as a trusted proxy and routing hub. It receives requests from providers, logs transactions in a multi-tenant ledger, and forwards data to the correct regulatory agent (CMS).

### 3. CMS Attestation Agent (GCP)

The core validator. It uses **Vertex AI (Gemini 1.5 Flash)** to perform semantic validation on healthcare data. Once validated, it issues a **W3C Verifiable Credential** signed with an **Ed25519** private key.

### 4. Payer Agent (AWS / GCP)

The final decision node. It receives a "Prior Authorization" request from the Provider, accompanied by the CMS Verifiable Credential. It verifies the cryptographic proof against the global Trust Registry and auto-approves compliant requests.

### 5. PBM Agent (GCP)

Managed by Pharmacy Benefit Managers. It validates medication eligibility, formulary compliance, and drug-drug interactions for pharmacy attestations.

### 6. Lab (Diagnostic) Agent (GCP)

Provides authoritative attestations for lab results (e.g., HbA1c) and imaging reports, ensuring diagnostic evidence is cryptographically bound to patient identity.

### 7. Auditor Agent (Governance)

Managed by regulatory bodies like HHS-OIG. It performs real-time oversight of the attestation ledger to detect anomalies and ensure system-wide compliance.

### 8. Credentialing Agent (Trust)

Verifies medical practitioner licensing (NPI) to ensure all clinical attestations originate from authorized and verified healthcare professionals.

### 9. Patient Empowerment Agent (Ownership)

Represents the patient in the A2A mesh. It manages patient consent and provides a personal vault for all Verifiable Credentials issued about the patient.

### 10. Clinical Research Agent (Innovation)

Uses Gemini 1.5 Flash to autonomously match patients to high-impact clinical trials using cryptographically verified health data.

## Multi-Cloud Strategy

The system is designed for maximum interoperability:

- **AWS**: Ideal for legacy Payer systems and S3-based data triggers.
- **GCP**: Leverages Vertex AI for semantic analysis and Firestore for the global attestation ledger.
- **Interoperability**: Agents communicate using **JSON-RPC 2.0** over HTTPS, ensuring cloud-agnostic compatibility.

## Trust Model

Security is built on Decentralized Identity (DID) and Cryptographic Proofs:

- **Trust Registry**: A centralized source of truth for agent DIDs and public keys.
- **Ed25519 Signatures**: Every attestation is signed by CMS, ensuring data integrity and non-repudiation.
- **VC Lifecycle**: Attestations follow the W3C Verifiable Credential standard, making them portable and machine-verifiable.
