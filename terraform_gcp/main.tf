terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  default     = "us-central1"
}

variable "project_name" {
  default = "cms-a2a-attestation"
}

# --- Firestore (Multitenant Ledger) ---
resource "google_firestore_database" "ledger" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# --- Storage Bucket for function code ---
resource "google_storage_bucket" "function_bucket" {
  name     = "${var.project_id}-functions"
  location = var.region
  force_destroy = true
}

# --- IAM for AI Platform (Vertex AI) ---
resource "google_service_account" "function_sa" {
  account_id   = "a2a-functions-sa"
  display_name = "Service Account for A2A Cloud Functions"
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

# Add Firestore permissions
resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.function_sa.email}"
}

# --- Cloud Functions Definitions ---

# CMS Agent
resource "google_cloudfunctions2_function" "cms_agent" {
  name        = "${var.project_name}-cms"
  location    = var.region
  
  build_config {
    runtime     = "python311"
    entry_point = "cms_agent"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.cms_zip.name
      }
    }
  }

  service_config {
    max_instance_count = 10
    available_memory   = "256Mi"
    timeout_seconds    = 60
    service_account_email = google_service_account.function_sa.email
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }
}

# Clearinghouse Agent
resource "google_cloudfunctions2_function" "clearinghouse" {
  name        = "${var.project_name}-clearinghouse"
  location    = var.region
  
  build_config {
    runtime     = "python311"
    entry_point = "clearinghouse_agent"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.ch_zip.name
      }
    }
  }

  service_config {
    max_instance_count = 10
    available_memory   = "256Mi"
    timeout_seconds    = 60
    service_account_email = google_service_account.function_sa.email
    environment_variables = {
      GCP_PROJECT      = var.project_id
      CMS_A2A_ENDPOINT = google_cloudfunctions2_function.cms_agent.url
    }
  }
}

# --- Cloud Storage for Claim Triggers (Phase 3) ---
resource "google_storage_bucket" "claims_dropbox" {
  name     = "${var.project_id}-claims-dropbox"
  location = var.region
  force_destroy = true
}

# --- Payer Agent Cloud Function (Phase 3) ---
resource "google_cloudfunctions2_function" "payer_agent" {
  name        = "${var.project_name}-payer"
  location    = var.region
  
  build_config {
    runtime     = "python311"
    entry_point = "payer_agent"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.payer_zip.name
      }
    }
  }

  service_config {
    max_instance_count = 10
    available_memory   = "256Mi"
    timeout_seconds    = 60
    service_account_email = google_service_account.function_sa.email
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }
}

# --- Zip objects (Update for Phase 3) ---
resource "google_storage_bucket_object" "payer_zip" {
  name   = "payer_agent.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = "${path.module}/payer_agent.zip"
}

# --- Update Clearinghouse ENV for Phase 3 ---
resource "google_cloudfunctions2_function" "clearinghouse" {
  name        = "${var.project_name}-clearinghouse"
  location    = var.region
  
  build_config {
    runtime     = "python311"
    entry_point = "clearinghouse_agent"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.ch_zip.name
      }
    }
  }

  service_config {
    max_instance_count = 10
    available_memory   = "256Mi"
    timeout_seconds    = 60
    service_account_email = google_service_account.function_sa.email
    environment_variables = {
      GCP_PROJECT      = var.project_id
      CMS_A2A_ENDPOINT = google_cloudfunctions2_function.cms_agent.url
      PAYER_A2A_ENDPOINT = google_cloudfunctions2_function.payer_agent.url
    }
  }
}

# --- Cloud Storage Trigger for Provider ---
# In production, this would use google_eventarc_trigger
# For this demo, we'll mark the architecture as 'Event-Ready'

# Outputs
output "clearinghouse_url" {
  value = google_cloudfunctions2_function.clearinghouse.url
}

output "claims_bucket_gcp" {
  value = google_storage_bucket.claims_dropbox.name
}
