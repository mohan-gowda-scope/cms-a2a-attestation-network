# API Reference (JSON-RPC 2.0)

All agent-to-agent communication is performed via JSON-RPC 2.0 over HTTPS.

## CMS / Clearinghouse Methods

### `attest_healthcare_data`

Used by the Provider or Clearinghouse to request a compliance attestation from CMS.

**Request Params:**

- `provider_id` (string): The DID or unique ID of the provider.
- `patient_id` (string): The patient identifier.
- `fhir_bundle` (object): A valid FHIR R4 Bundle resource.

**Successful Response:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "attestation_id": "uuid",
    "status": "Compliant",
    "verifiable_credential": { ... }
  },
  "id": "req-1"
}
```

## Payer Methods

### `request_prior_auth`

Used by providers to request authorization for medical services.

**Request Params:**

- `provider_id` (string): The provider's ID.
- `patient_id` (string): The patient's ID.
- `verifiable_credential` (object): The signed CMS VC.
- `clinical_data` (object): CPT codes and encounter details.

**Successful Response:**

```json
{
  "jsonrpc": "2.0",
  "result": {
    "auth_id": "GCP-AUTH-XXXXXX",
    "status": "Auto-Approved",
    "notes": "Verified via CMS Trust Hub"
  },
  "id": "req-2"
}
```

## Error Codes

- `-32600`: Invalid Request (Malformed JSON-RPC)
- `-32601`: Method not found
- `-32602`: Invalid params (Missing VC or data)
- `-32000`: Cryptographic Verification Failed
