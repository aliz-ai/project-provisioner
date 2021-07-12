#!/bin/bash

projects_budgets_for_billing_account() {
    BA_NO="$1"
    BA_NAME="$2"
    F_BA_NAME=`sed 's/ /_/g' <<<$BA_NAME`
    P_LIST=`gcloud alpha billing projects list --billing-account=$BA_NO --format=json` && \
        B_LIST=`gcloud alpha billing budgets list --billing-account=$BA_NO --format="json(name,displayName,budgetFilter.projects,amount)"` && \
        echo "{\"projects\": $P_LIST, \"budgets\": $B_LIST, \"billing_account_name\": \"$BA_NAME\", \"billing_account_number\": \"$BA_NO\"}" >".target/accounts/$F_BA_NAME".json
}

rm -rf ".target"
mkdir -p ".target/accounts"
gcloud projects list --format=json > ".target/all_projects.json"
BILLING_ACCOUNTS=`gcloud alpha billing accounts list --filter="open=True" --format="csv[no-heading](name,displayName)"`
while IFS="," read -r BA_NO BA_NAME; do
    projects_budgets_for_billing_account "$BA_NO" "$BA_NAME"
done <<< "$BILLING_ACCOUNTS"

