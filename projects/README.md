# Projects configuration

Terraform needs the list of the projects as a variable in order to be able to manage them. However, as we already have a few hundreds of projects maintaining this in a single file wouldn't be to comfortable and the risk of human error is pretty high as everyone should modify the same file.

Thus, the decision was made to split the list of projects into individual files (that can be JSON or YAML) objects stored in individual files and implement a script that is able to vaildate these files and create the project list variable in the terraform variables file.

This folder contains these individual JSON or YAML files.

## Directory structure

In the first iteration we have only the `all_projects` directory that contains all of our projects. However, later on we might want to distinguish between different type of projects and manage them differently in Terraform (like sandbox projects, customer projects, etc.). In this case the different project types can get different directories.

## JSON and YAML structure

### Templates

You can find examples for absolute minimum configurations in the `templates` folder. The current templates are the following:

| Name | Description |
|------|-------------|
| sandbox | A template for sandbox projects. |

### Fields description

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `project` | Yes | `string` | Unique identifier of the prroject within the domain. By default, this is going to be used for project ID. |
| `project_id` | No | `string` | Introduced for being able to support backward compatibility with future featrues that might use automatic prefixing/suffixing for project IDs |
| `project_name` | No | `string` | The name to use for the project. By default it's the same as `project` |
| `billing_account_id` | No | `string` | The ID of the billing account. The list of the existing billing accounts and their usage [can be found here](https://sites.google.com/doctusoft.com/intranet/engineering/gcp-policy). You can omit this setup to disable billing. In this case you should omit the `budget` section as well. |
| `folder_id` | No | `string` | In case the project is not directly under the organization level, the parent folder ID should be specified |
| `owners` | Yes | `string[]` | The list of the initial owners of the project. The purpose of this list is to ensure that someone except the used service account is going to be owner of the project within the organization. |
| `labels` | Yes | `object` | A map containing the labels to add to the project. The  [GCP policy](https://sites.google.com/doctusoft.com/intranet/engineering/gcp-policy) defines the required labels. Unless these labels are set, the PR cannot be approved. |
| `budget` | No | `object` | The definition of the budget to create for the project. To disable billing, omit this configuration along with the `billing_account_id`. |
| `budget.display_name` | No | `string` | Display name of the budget. Defaults to `Budget for project: <project ID>` |
| `budget.credit_types_treatment` | No | `enum` | Documented [here](https://cloud.google.com/billing/docs/reference/budget/rest/v1beta1/billingAccounts.budgets#CreditTypesTreatment). Defaults to `EXCLUDE_ALL_CREDITS` |
| `budget.currency` | Yes | `string` | Currency of the limit definition |
| `budget.limit` | Yes | `number` | The actual limit amonut |
| `budget.all_updates_rule` | No | `object` | Rules to apply to all updates to the actual spend, regardless of the thresholds set in threshold_rules. |
| `budget.all_updates_rule.disable_default_iam_recipients` | No | `boolean` | When set to true, disables default notifications sent when a threshold is exceeded. |
| `budget.all_updates_rule.schema_version` | No | `string` | The schema version of the notification sent to pubsub_topic. Only "1.0" is accepted. |
| `budget.all_updates_rule.pubsub_topic` | No | `string` | The name of the Pub/Sub topic where budget related messages will be published, in the form **projects/{project_id}/topics/{topic_id}**. |
| `budget.all_updates_rule.monitoring_notification_channels` | Yes (if `budget.all_updates_rule` is defined) | `string[]` | Targets to send notifications to when a threshold is exceeded. |
| `budget.threshold_rules` | No | `object[]` |  Rules that trigger alerts when spend exceeds the specified percentages of the budget. Defaults to: <br>90% current spend<br>100% forcasted spend<br> 100% actual spend |
| `budget.threshold_rules.spend_basis` | Yes | `enum` | Either `CURRENT_SPEND` or `FORECASTED_SPEND` |
| `budget.threshold_rules.threshold_percent` | Yes | `number` | The percent after the notification is sent in decimal format (e.g. 50% -> 0.5). |
