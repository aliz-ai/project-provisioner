import json
import yaml
import os
import csv
from datetime import datetime

ignored_json_directories = ['templates']

def load_dict(file_name):
    """
    Reads JSON or YAML file into a dictionary
    """
    if file_name.lower().endswith(".json"):
        with open(file_name) as _f:
            return json.load(_f)

    with open(file_name) as _f:
        return yaml.full_load(_f)


def load_billing_info(project_id, project_number, billing_info):
    """
    Returns the billing related information by project ID
    """
    res = {
        'project_id': project_id,
        'project_number': project_number,
        'billing_enabled': False,
        'billing_account_name': '',
        'billing_account_number': '',
        'budget_defined': False,
        'budget_id': '',
        'budget_amount': 0,
        'budget_ccy': 'USD',
        'budget_details': ''
    }

    for ba_name in billing_info:
        p = next((p for p in billing_info[ba_name]['projects'] if project_id == p['projectId']), None)
        if p is None:
            continue

        res['billing_enabled'] = p['billingEnabled']
        res['billing_account_name'] = billing_info[ba_name]['billing_account_name']
        res['billing_account_number'] = billing_info[ba_name]['billing_account_number']

        b = next((b for b in billing_info[ba_name]['budgets'] 
            if 'budgetFilter' in b 
            and 'projects' in b['budgetFilter'] 
            and len(b['budgetFilter']['projects']) 
            and f'projects/{project_number}' in b['budgetFilter']['projects']), None)

        if b is None:
            break
        
        res['budget_id'] = b['name']
        res['budget_defined'] = True
        res['budget_amount'] = b['amount']['specifiedAmount']['units']
        res['budget_ccy'] = b['amount']['specifiedAmount']['currencyCode']
        res['budget_details'] = json.dumps(b)
        break

    return res


if __name__ == '__main__':
    directory = os.getcwd()
    projects_root = "../../projects"
    
    # prepare the list of all the JSON and YAML files below the projects folder
    p_definitions = []
    for root, dirs, files in os.walk(projects_root):
        if os.path.basename(root) not in ignored_json_directories:
            p_definitions = ["{}/{}/{}".format(directory, root, f) for f in files if f.lower().endswith('.json') or f.lower().endswith('.yaml')]

    # create a project_id => {project details} dictionary about the managed projects
    managed_projects = {}
    for p_definition in p_definitions:
        p_obj = load_dict(p_definition)
        managed_projects[p_obj.get('project_id', p_obj['project'])] = p_obj

    # load all the projects from GCP console
    all_projects =  load_dict(f'{directory}/.target/all_projects.json')

    # load the project lists into a billing_account_name => {details} dictionary
    files = os.listdir(f'{directory}/.target/accounts')
    billing_info = {}
    for f in files:
        ba_name = f[:-5]
        billing_info[ba_name] = load_dict(f'{directory}/.target/accounts/{f}')
    

    current_datetime = datetime.now()
    ts = current_datetime.astimezone().isoformat()

    report_data = []
    for p in all_projects:
        project_id = p['projectId']
        project_number = p['projectNumber']

        project_info = load_billing_info(project_id, project_number, billing_info)
        project_info['timestamp'] = ts
        project_info['project_id'] = project_id
        project_info['project_number'] = project_number
        project_info['parent_type'] = "" if "parent" not in p else p['parent']['type']
        project_info['parent_id'] = "" if "parent" not in p else p['parent']['id']
        project_info['lifecycle_state'] = p['lifecycleState']
        project_info['labels'] = "" if "labels" not in p else json.dumps(p['labels'])

        project_info['managed_by_terraform'] = True if project_id in managed_projects else False
        
        report_data.append(project_info)

    with open('.target/projects-report.csv', 'w') as csvfile:
        fieldnames = ['timestamp', 'project_id', 'project_number', 'parent_type', 'parent_id',
            'lifecycle_state', 'labels', 'managed_by_terraform', 'billing_enabled', 
            'billing_account_name', 'billing_account_number', 'budget_defined', 'budget_id', 
            'budget_amount', 'budget_ccy', 'budget_details']
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data)