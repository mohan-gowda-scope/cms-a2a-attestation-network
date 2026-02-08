# --- GCP AGENT MESH (10 AGENTS) ---

locals {
  is_gcp = var.cloud_provider == "gcp"
}

# --- 10 Agent Definitions (Cloud Run) ---
# For simplicity in this demo, we use a single container image that routes via method
resource "google_cloud_run_v2_service" "gcp_agents" {
  for_each = local.is_gcp ? toset(local.agent_list) : []
  name     = "a2a-${each.key}-gcp"
  location = "us-central1"

  template {
    containers {
      image = "gcr.io/google-samples/hello-app:1.0" # Placeholder for deployment
      env {
        name  = "AGENT_TYPE"
        value = each.key
      }
      env {
        name  = "CLOUD_PROVIDER"
        value = "gcp"
      }
    }
  }
}

# Vertex AI Access (Parity with Bedrock)
resource "google_project_service" "vertex_ai" {
  count   = local.is_gcp ? 1 : 0
  service = "aiplatform.googleapis.com"
}
