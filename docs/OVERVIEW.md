# Project Overview: CMS A2A Attestation Network

## Mission

The CMS A2A (Agent-to-Agent) Attestation Network is a next-generation healthcare data validation system. It enables autonomous, cryptographically secure validation of healthcare attestations between providers, payers, and regulatory bodies (CMS) without manual intervention.

## 🌈 The Choice: Dual-Stack Architecture

Unlike traditional monolithic systems, the CMS A2A Network is **cloud-native and provider-agnostic**. Customers can deploy the entire 10-agent ecosystem on their platform of choice:

- **AWS Stack**: High-performance orchestration using **Lambda**, **Bedrock (Anthropic Claude 3.5)**, and **DynamoDB**.
- **GCP Stack**: Native AI integration using **Cloud Run**, **Vertex AI (Gemini 1.5 Flash)**, and **Firestore**.

## Key Components (The 10-Agent Swarm)

### 1. Provider Agent

Initiates the attestation flow when clinical data (FHIR bundles) is received. It orchestrates the process and stores the final approval.

### 2. Clearinghouse Agent

Acts as the network's high-traffic routing hub, ensuring requests are logged and routed to the correct regulatory agent.

### 3. CMS Attestation Agent

The core validator. Uses AI (Bedrock or Vertex) to perform semantic validation on healthcare data. Issues **W3C Verifiable Credentials** signed with **Ed25519**.

### 4. Payer Agent

The decision node. Verifies the CMS Verifiable Credential and auto-approves compliant prior authorization requests.

### 5. PBM Agent (Pharmacy)

Validates medication eligibility and formulary compliance for pharmacy attestations.

### 6. Lab Agent (Diagnostics)

Provides authoritative attestations for lab results and imaging, binding evidence to patient identity.

### 7. Auditor Agent (Governance)

Performs real-time oversight of the attestation ledger to ensure system-wide compliance and anomaly detection.

### 8. Credentialing Agent (Trust)

Verifies medical practitioner licensing (NPI) against global registries.

### 9. Patient Proxy Agent

Represents the patient's interests, managing consent and providing a self-sovereign vault for health credentials.

### 10. Clinical Research Agent (Innovation)

Autonomously matches patients to clinical trials using cryptographically verified clinical findings.

## Trust Model

Security is built on Decentralized Identity (DID) and Cryptographic Proofs:

- **Identity Parity**: Agents have the same cryptographic identity (`did:web`) regardless of which cloud they run on.
- **Ed25519 Signatures**: Every attestation is signed, ensuring non-repudiation across the entire journey.
- **Machine Verifiable**: No human review is required; the network is "Zero Trust" by design.
