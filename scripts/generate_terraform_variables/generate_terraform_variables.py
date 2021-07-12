import json
import yaml
import os
import re

key_error_message = 'attribute is required but not found'

ignored_json_directories = ['templates']

project_id_set = []

default_project_settings = {}

def load_dict(file_name):
    """
    Reads JSON or YAML file into a dictionary
    """
    if file_name.lower().endswith(".json"):
        with open(file_name) as _f:
            return json.load(_f)

    with open(file_name) as _f:
        return yaml.full_load(_f)


def validate(json_file, terraform_project):
    """
    Validates the project configuration - exclusively technical validation, no business rules enforced
    """

    # project attribute is required
    if 'project' not in terraform_project:
        raise KeyError(f'`project` {key_error_message} in {json_file}')

    # the project_id should be unique (universally, but we check at least within the org)
    project_id = terraform_project['project'] if 'project_id' not in terraform_project else terraform_project['project_id']
    if project_id in project_id_set:
        raise KeyError(f'project {project_id} already exists')

    project_id_set.append(project_id)

    # at least one initial owner should be specified
    if 'owners' not in terraform_project:
        raise KeyError(f'owners {key_error_message} or empty in {json_file}')

    # if billing account is not provided no budget should be specified, otherwise budget is mandatory
    if 'billing_account_id' not in terraform_project:
        if 'budget' in terraform_project:
            raise KeyError(f'budget should not be specified when billing_account_id is not specified!')
    else:
        if 'budget' not in terraform_project:
            raise KeyError(f'budget {key_error_message}')

        if 'currency' not in terraform_project['budget']:
            raise KeyError(f'budget.currency {key_error_message} in {json_file}')

        if 'limit' not in terraform_project['budget']:
            raise KeyError(f'budget.limit {key_error_message} in {json_file}')

    label_key_regex = "^[a-z][a-zA-Z0-9_-]{0,62}$"
    label_value_regex = "^[a-zA-Z0-9_-]{0,63}$"

    labels = terraform_project.get('labels', {})
    for key, value in labels.items():
        if not bool(re.match(label_key_regex, key)):
            raise KeyError(f'label key {key} is invalid in {json_file}')

        if not bool(re.match(label_value_regex, value)):
            raise KeyError(f'label value {value} is invalid in {json_file}')



def set_default_values(json_file, terraform_project):
    """
    Set default values
    """
    new_project = default_project_settings.copy()
    new_project.update(terraform_project)

    # FIXME - update() is shallow, not elegant, but we want to apply the defaults for the budget conf. as well
    new_project['budget'] = default_project_settings['budget'].copy()
    new_project['budget'].update(terraform_project.get('budget', {}))

    return {
        new_project['project']: new_project
    }


if __name__ == '__main__':
    directory = os.getcwd()
    projects_root = "../../projects"

    # load default_project_settings
    default_project_settings = load_dict("default_project_settings.json")
    
    # prepare the list of all the JSON files below the projects folder
    p_definitions = []
    for root, dirs, files in os.walk(projects_root):
        if os.path.basename(root) not in ignored_json_directories:
            p_definitions.extend(["{}/{}/{}".format(directory, root, f) for f in files if f.lower().endswith('.json') or f.lower().endswith('.yaml')])

    # create a project_type => projects[] dictionary where the type is the parent folder of the json file
    projects_dict = {}
    for p_definition in p_definitions:
        p_type = os.path.basename(os.path.dirname(p_definition))
        p_obj = load_dict(p_definition)
        validate(p_definition, p_obj)

        if p_type not in projects_dict:
            projects_dict[p_type] = {}

        projects_dict[p_type].update(set_default_values(p_definition, p_obj))

    # read the common variables and update that with the generated projects variables then save it
    common_vars_file = f'{directory}/../../terraform/environments/prod/common_vars.json'
    out_vars_file = f'{directory}/../../terraform/environments/prod/generated_vars.json'
    config = load_dict(common_vars_file)
    config.update(projects_dict)

    with open(out_vars_file, 'w') as output_file:
        output_file.write(json.dumps(config, indent=2))
