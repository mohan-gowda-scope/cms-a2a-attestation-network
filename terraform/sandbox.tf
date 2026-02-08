# CMS A2A Network Sandbox Infrastructure
# Optimized for ephemeral, low-cost trials

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

resource "google_cloud_run_v2_service" "sandbox_ecosystem" {
  name     = "a2a-trust-sandbox"
  location = "us-central1"
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = "gcr.io/${var.project_id}/a2a-node-orchestrator:latest"
      
      env {
        name  = "ENV"
        value = "SANDBOX"
      }
      
      env {
        name  = "FIRESTORE_COLLECTION"
        value = "sandbox_attestations"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
    
    # Enable request-based scaling to 0 when idle
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "sandbox_public" {
  location = google_cloud_run_v2_service.sandbox_ecosystem.location
  project  = google_cloud_run_v2_service.sandbox_ecosystem.project
  name     = google_cloud_run_v2_service.sandbox_ecosystem.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "sandbox_endpoint" {
  value = google_cloud_run_v2_service.sandbox_ecosystem.uri
}
