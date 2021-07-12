terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 3.58.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = ">= 3.58.0"
    }
  }
}

provider "google" {
  project = var.project
  region  = var.default_region
  zone    = var.default_zone
}

provider "google-beta" {
  project = var.project
  region  = var.default_region
  zone    = var.default_zone
}

module "projects" {
  source                = "./modules/projects"
  organization_id       = var.organization_id
  projects              = var.all_projects
}