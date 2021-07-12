# Terraform project

In this toolchain Terraform is responsible to create the GCP projects, setup initial ownerships and define budgets for them.

## How to setup

Setup your environment-specific variables in `environments/prod/common_vars.json` file as follows

| Variable name | Description | Example value |
|---------------|-------------|---------------|
| `project` | The ID of the GCP project dedicated to the tool. | `gcp-project-provisioning` |
| `organization_id` | The numeric ID of your organization on GCP. | `123456789012345` |
| `default_region` | The default compute region to use. | `europe-west3` |
| `default_zone` | The default compute zone to use. | `europe-west3-b` |

Setup your terraform backend in `environments/prod/backend-config.properties` file as follows

| Variable name | Description | Example value |
|---------------|-------------|---------------|
| `bucket` | The name of the GCP bucket in which the terraform state file should be stored | `gcp-project-provisioning-tf-state` |
| `prefix` | The optional subfolder to use | `env/prod` |

## Used versions
**Terraform version:** `0.14.7`

**Providers:**
 * google `>= 3.58.0`
 * google-beta `>= 3.58.0`

## Terraform variables

As maintaining the setup of hundreds of GCP projects can be problematic in a single file, each project has it's own JSON or YAML configuration. This also means that we need a script that is able to merge this information and store that as a variable in the terraform variable file.

The `generate_terraform_variables` python script is responsible for this task. The script reads the `common_vars.json` file (found under the environment directory) and the project JSON & YAML files and creates a `generated_vars.json` file that can be used with terraform.


