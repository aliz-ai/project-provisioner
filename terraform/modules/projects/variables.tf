variable "projects" {
  type = map(
    object(
      {
        project            = string,
        project_number     = string,
        project_id         = string,
        project_name       = string,
        folder_id          = string,
        billing_account_id = string,
        owners             = set(string),
        budget = object(
          {
            display_name           = string,
            credit_types_treatment = string,
            currency               = string,
            limit                  = string,
            all_updates_rule = object(
              {
                disable_default_iam_recipients   = bool,
                schema_version                   = string,
                pubsub_topic                     = string,
                monitoring_notification_channels = list(string)
              }
            ),
            threshold_rules = list(object(
              {
                spend_basis       = string,
                threshold_percent = number
              }
            ))
          }
        ),
        labels = map(string)
      }
    )
  )
  description = "The basic setup of the projects to create"
}

variable "project_type" {
  type        = string
  default     = ""
  description = "The type of the project"
}

variable "project_postfix" {
  type        = string
  default     = ""
  description = "The postfix for the project ID to append"
}

variable "organization_id" {
  type        = string
  description = "The organization ID where the projects are present"
}

locals {
  po_mapping            = [for v in values(var.projects) : { for o in v.owners : "${v.project}:${o}" => { project : v.project, owner : o } }]
  projects_with_billing = { for k, v in var.projects : k => v if v.billing_account_id != "" }
  project_ownerships    = merge(flatten([local.po_mapping])...)
}
