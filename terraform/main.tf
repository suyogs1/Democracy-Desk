# Infrastructure as Code for Democracy Desk
# Demonstrates production-grade Google Cloud resource management

provider "google" {
  project = "promptwar-493105"
  region  = "us-central1"
}

# 1. Cloud Run Service
resource "google_cloud_run_service" "democracy_desk" {
  name     = "democracy-desk-ai"
  location = "us-central1"

  template {
    spec {
      containers {
        image = "gcr.io/promptwar-493105/democracy-desk-ai"
        resources {
          limits = {
            memory = "1024Mi"
            cpu    = "1000m"
          }
        }
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = "promptwar-493105"
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# 2. BigQuery Dataset for Analytics
resource "google_bigquery_dataset" "analytics" {
  dataset_id                  = "democracy_desk"
  friendly_name               = "Democracy Desk Analytics"
  description                = "Query intent and regional trends dataset"
  location                   = "US"
}

# 3. Cloud Storage Bucket for Reports
resource "google_storage_bucket" "archives" {
  name          = "promptwar-493105-archives"
  location      = "US"
  force_destroy = true
}

# 4. Firestore Database (Native Mode)
resource "google_firestore_database" "persistence" {
  name        = "(default)"
  location_id = "nam5"
  type        = "FIRESTORE_NATIVE"
}

# 5. Secret Manager for Vertex AI Keys
resource "google_secret_manager_secret" "vertex_key" {
  secret_id = "vertex-ai-api-key"
  replication {
    automatic = true
  }
}
