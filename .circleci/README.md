# CICD workflows

The CICD pipelines are implemented for CircleCI.

## How to setup

To get the CircleCI pipelines work, you have to define the following project-level environment variables in CircleCI:

| Variable name | Description |
|---------------|-------------|
| `GOOGLE_CREDENTIALS` | The key file of the Service Account to use in JSON format. |
| `GOOGLE_PROJECT_ID` | The ID of the GCP project dedicated to this tool. |
| `REPORTS_GCS_BUCKET` | The name of the GCS bucket where the CSV reports should be stored. |

## `create_plan` workflow

**Triggered**: on each commit on each branch except the `master`

**Purpose**: validating the changes and show the impact on the actual deployment to make it possible to review.

**Implementation**: perpares the terraform variables from the individual project configuration files using the `generate_terraform_variables` python script and executes a `terraform plan` command displaying the plan details in the logs. During the review of the PR on the specific branch the reviewer shoul check this plan in the logs.

## `apply_changes` workflow

**Triggered**: on each commit on the `master` branch

**Purpose**: applying the requested changes to the infrastructure

**Implementation**: perpares the terraform variables from the individual project configuration files using the `generate_terraform_variables` python script and executes a `terraform apply` command. After the successful apply, it creates the report about the projects into a CSV file with the `generate_status_csv` python script and uploads that to GCS.

## `generate_daily_report` workflow

**Triggered**: automatically at 4am each day

**Purpose**: providing up-to-date information about the Terraform managed projects and the manually created ones. Later this can be used for alerting if someone creates a project manually instead of the standard way.

**Implementation**: Using the `generate_status_csv` scripts it generates the CSV report and uploads that to GCS.