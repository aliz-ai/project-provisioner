# Supporting scripts

## generate_reports

The purpose of these scripts is to povide enough information to make it possible to keep the GCP setup clean.

The `collect.sh` is a bash script that uses `gcloud` CLI to collect information through the GCP APIs and saves them into JSON files such as:

1. The list of all of the projects
2. The list of the billing accounts
3. The list of the projects and budgets for each billing account

### generate_status_csv.py

The purpose of this report is to generate a CSV that provides a good enough overview about the managed and unmanaged GCP projects. The script reads the JSON files along with the project configuration files (JSONs and YAMLs) and outputs a CSV with the following columns:

| Column name | Column description |
|-------------|--------------------|
| `timestamp` | The timestamp of the report generation |
| `project_id` | The GCP project's ID |
| `project_number` | The GCP project's number |
| `parent_type` | `organization` or `folder` |
| `parent_id` | The organization's or the parent folder's ID |
| `lifecycle_state` | Enum, possible values are [documented here](https://cloud.google.com/resource-manager/reference/rest/v1/projects#lifecyclestate) |
| `labels` | The labels defined on the project (in a JSON structure) |
| `managed_by_terraform` | Whether the project is managed by this tool or not |
| `billing_enabled` | Whether the project is assigned to any of the organization's billing accounts |
| `billing_account_name` | The name of the billing account the project is assigned to |
| `billing_account_number` | The ID of the billing account the project is assigned to |
| `budget_defined` | Whether a budget is defined for the project or not |
| `budget_id` | The ID of the defined budget |
| `budget_amount` | The limit amount of the defined budget |
| `budget_ccy` | The currency of the defined budget |

### generate_budgets_csv.py

The purpose of this report is to generate a CSV that lists the budgets that might be outdated. It lists the budgets with any of the following properties:

 - The budget has no projects specified
 - The budget has projects specified, but the pojects cannot be found within the organization

Outputs a CSV with the following columns:

timestamp,billing_account_name,billing_account_number,budget_dislpay_name,budget_id,budget_string,message

| Column name | Column description |
|-------------|--------------------|
| `timestamp` | The timestamp of the report generation |
| `billing_account_name` | The name of the billing account the budget belongs to |
| `billing_account_number` | The number of the billing account the budget belongs to |
| `budget_dislpay_name` | The display name of the budget |
| `budget_id` |The ID of the budget |
| `budget_string` | The full JSON representation of the budget |
| `message` | The message that describes why the budget is enlisted in the report |

## generate_terraform_variables

Terraform needs the list of the projects to manage within a variable, however, maintaining hundreds of GCP projects in a single file can be troublesome. This is the reason why the decision was made to split the configuration in a way that all project has its own JSON or YAML file.

The purpose of this script is to read all of these individual files and merge them with the standard terraform variables (like org. ID, billing account IDs, etc.). This is used in the CICD pipeline.