# GCP project provisioner tool

GCP project creation within Aliz was not always a standardized process. As we grew we realized that the number of our GCP projects grew as well to a level that is hard to manually manage and control. We wanted to introduce automation, enforce organization standards and implement an approval process for creating new GCP projects - and this tool was born.

## What is this tool actually doing?

1. Implements a project creation approval workflow through Github pull requests
2. Once a project creation request gets approved, the tool creates the necessary GCP resources:
    - GCP project with the proper metadata & billing configuration
    - Budget with proper notification setup
3. Creates nightly reports in CSV format to GCS (see the details [here](scripts/README.md))

## How to install this into my domain?

1. Create a dedicated GCP project that will host the resources needed by the tool:
   - Create dedicated service account. This service account is going to be used by the tool, so you need to grant the following roles:
     - Billing Account Costs Manager (`roles/billing.costsManager`)
     - Project Billing Manager (`roles/billing.projectManager`)
     - Project Creator (`roles/resourcemanager.projectCreator`)
     - Project IAM Admin (`roles/resourcemanager.projectIamAdmin`)
     - Browser (`roles/browser`)
   - Create a GCS bucket that is going to hold the terraform state file
   - Optionally create a dedicated GCS bucket for the CSV reports
   - Enable the following APIs in the project:
     - Compute Engine API (`compute.googleapis.com`)
     - Cloud Resource Manager API (`cloudresourcemanager.googleapis.com`)
     - Cloud Billing API (`cloudbilling.googleapis.com`)
     - Cloud Billing Budget API (`billingbudgets.googleapis.com`)
2. Fork this repository
2. Configure the terraform project as described [here](terraform/README.md)
3. Configure the CICD pipeline as described [here](.circleci/README.md)
4. Create your own template JSON and YAML files in `projects/templates` directory to support your users

## How to use the tool?

### As a requestor
As a requestor, follow the following steps:

1. Create your project request prepared in a JSON or YAML file under the `projects/all_projects` directory. To get started, pick one of the templates with an absolute minimum configuration from the `projects/templates` directory. For a detailed description of the configuration structure, scroll down a bit more!
2. Push this to a feature branch
3. Create a PR
4. Check if the CICD pipeline gave green light and fix the problems if there's any
5. Fix the changes requested by the approvers
6. Once your branch gets merged, the deloyment will be performed in a few minutes.


### As an approver

1. Check if the CICD workflow was successful on the branch. If not, ignore, otherwise proceed!
2. Open the CICD workflow `tf_plan` job's details in CircleCI. Check if the changes make sense. On a request for a new project you have to see
   - a new GCP project
   - a new budget for the new project
   - one or more project ownership IAM bindings
   - and **no change in other resources**
3. Once everything is fine, approve and merge the PR
4. The CICD pipeline on the `master` branch will apply the terraform configuration
5. After applying the configuration the contents of the report is going to be updated


## Tech details

| Directory | Docs | Purpose |
|-----------|------|---------|
| `.circleci` | [docs](.circleci/README.md) | Contains the CICD pipeline implementation | 
| `projects` | [docs](projects/README.md) | Contains the project configuration JSON or YAML files |
| `scripts` | [docs](scripts/README.md) | Contains shell and python scripts used for automation |
| `terraform` | [docs](terraform/README.md) | Contains the terraform project |

## You need more?

If you are looking for a more advanced solution please have a look at our Platform: https://aliz.ai/product-landing-page/
If you are looking for ready-made blueprints what you can checkout and adjust the code to your needs: https://aliz.ai/blueprints/
