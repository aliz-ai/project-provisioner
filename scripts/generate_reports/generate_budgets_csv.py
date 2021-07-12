import json
import yaml
import os
import csv
from datetime import datetime

def load_dict(file_name):
    """
    Reads JSON or YAML file into a dictionary
    """
    if file_name.lower().endswith(".json"):
        with open(file_name) as _f:
            return json.load(_f)

    with open(file_name) as _f:
        return yaml.full_load(_f)


if __name__ == '__main__':
    directory = os.getcwd()

    # load all the projects from GCP console
    all_projects =  load_dict(f'{directory}/.target/all_projects.json')
    all_project_numbers = set(["projects/{}".format(p['projectNumber']) for p in all_projects])

    # load the project lists into a billing_account_name => {details} dictionary
    files = os.listdir(f'{directory}/.target/accounts')
    billing_info = {}
    for f in files:
        ba_name = f[:-5]
        billing_info[ba_name] = load_dict(f'{directory}/.target/accounts/{f}')
    

    current_datetime = datetime.now()
    ts = current_datetime.astimezone().isoformat()

    report_data = []
    for ba_name in billing_info:
        for b in billing_info[ba_name]['budgets']:
            if 'budgetFilter' not in b or 'projects' not in b['budgetFilter'] or len(b['budgetFilter']['projects']) == 0:
                report_data.append({
                    'timestamp': ts,
                    'billing_account_name': ba_name,
                    'billing_account_number': billing_info[ba_name]['billing_account_number'],
                    'budget_dislpay_name': b['displayName'],
                    'budget_id': b['name'],
                    'budget_string': json.dumps(b),
                    'message': 'No projects specified for this budget'
                })
                continue

            if not set(b['budgetFilter']['projects']).issubset(set(all_project_numbers)):
                report_data.append({
                    'timestamp': ts,
                    'billing_account_name': ba_name,
                    'billing_account_number': billing_info[ba_name]['billing_account_number'],
                    'budget_dislpay_name': b['displayName'],
                    'budget_id': b['name'],
                    'budget_string': json.dumps(b),
                    'message': 'Referenced project not found in domain'
                })

    with open('.target/budgets-report.csv', 'w') as csvfile:
        fieldnames = ['timestamp', 'billing_account_name', 'billing_account_number', 'budget_dislpay_name', 
            'budget_id', 'budget_string', 'message']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data)