resource "google_project" "PROJECT" {
  for_each = var.projects

  name            = coalesce(each.value.project_name, "${each.value.project}${var.project_type}${var.project_postfix}")
  project_id      = coalesce(each.value.project_id, "${each.value.project}${var.project_type}${var.project_postfix}")
  org_id          = each.value.folder_id == "" ? var.organization_id : ""
  folder_id       = each.value.folder_id
  billing_account = each.value.billing_account_id

  labels = each.value.labels
}

resource "google_billing_budget" "BUDGET" {
  depends_on = [google_project.PROJECT]

  provider = google-beta

  for_each        = local.projects_with_billing
  billing_account = each.value.billing_account_id
  display_name    = coalesce(each.value.budget.display_name, "Budget for project: ${google_project.PROJECT[each.key].project_id}")

  budget_filter {
    projects               = ["projects/${google_project.PROJECT[each.key].number}"]
    credit_types_treatment = each.value.budget.credit_types_treatment
  }

  amount {
    specified_amount {
      currency_code = each.value.budget.currency
      units         = each.value.budget.limit
    }
  }

  all_updates_rule = each.value.budget.all_updates_rule

  dynamic "threshold_rules" {
    for_each = each.value.budget.threshold_rules

    content {
      spend_basis       = threshold_rules.value.spend_basis
      threshold_percent = threshold_rules.value.threshold_percent
    }
  }
}

resource "google_project_iam_member" "PROJECT_OWNERSHIPS" {
  depends_on = [google_project.PROJECT]

  for_each = local.project_ownerships
  project  = "${each.value.project}${var.project_type}${var.project_postfix}"
  role     = "roles/owner"
  member   = each.value.owner
}
