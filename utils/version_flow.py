import os
import datetime
import builder
import config
from utils.clone_repo import clone_repo_with_name
from utils.build_binary import build_binary_and_move_for_joern, move_log_rule_file
from utils.helpers import print_timestamp
from utils.write_to_file import write_slack_summary


def check_update(github_token):
    cwd = os.getcwd()
    temp_dir = f'{cwd}/temp'

    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)

    # clone the first privado-core
    clone_repo_with_name(config.get_privado_core_url(github_token), builder.get_joern_privado_path("first"), "privado-core-enterprise")

    # clone second privado-core, used for updating the dependencies
    clone_repo_with_name(config.get_privado_core_url(github_token), builder.get_joern_privado_path("second"), "privado-core-enterprise")

    # change the permission
    os.system(f'chmod 777 {builder.get_joern_update_file_path("second")}')

    check_command = f'cd {builder.get_joern_privado_path("second")} && ./updateDependencies.sh --non-interactive --only=joern'
    output = os.popen(check_command).read()
    update_require = is_update_require(output)

    if update_require is None:
        return ["Error", "Error in fetching the Version"]
    if not update_require:
        return ["Updated", None]

    versions = get_updated_version(output)
    # clone privado for rules
    clone_repo_with_name(config.PRIVADO_RULE_URL, builder.get_privado_path(versions[0]), 'First - privado')
    clone_repo_with_name(config.PRIVADO_RULE_URL, builder.get_privado_path(versions[1]), 'Second - privado')
    return versions


def is_update_require(output):
    for line in output.split('\n'):
        if 'joern' in line:
            if 'unchanged' in line:
                return False
            else:
                return True
    return None


def get_updated_version(output):
    for line in output.split('\n'):
        if 'joern' in line:
            versions = line.split(':')[-1]
            older_version = versions.split('->')[0].strip()
            newer_version = versions.split('->')[1].strip()
            return [older_version, newer_version]
    return None


def build_binary_for_joern(versions):
    # Build binary for current version
    write_slack_summary(f'Current version: {versions[0]} \n Updated Version: {versions[1]} \n')
    try:
        build_binary_and_move_for_joern(f'{os.getcwd()}/temp/joern/first/privado-core-enterprise', config.BASE_CORE_BRANCH_KEY)
        move_log_rule_file(f'{os.getcwd()}/temp/joern/first/privado-core-enterprise/log4j2.xml', config.BASE_CORE_BRANCH_KEY)
    except Exception as e:
        print_timestamp(f'Binary generation failed for joern version {versions[0]}: ', e)
        write_slack_summary(f'Binary generation failed for joern version {versions[0]} \n {str(e)}')
        return False 

    try:
        build_binary_and_move_for_joern(f'{os.getcwd()}/temp/joern/second/privado-core-enterprise', config.HEAD_CORE_BRANCH_KEY)
        move_log_rule_file(f'{os.getcwd()}/temp/joern/second/privado-core-enterprise/log4j2.xml', config.HEAD_CORE_BRANCH_KEY)
    except Exception as e:
        print_timestamp(f'Binary generation failed for joern version {versions[1]}: ', e)
        write_slack_summary(f'Binary generation failed for joern version {versions[1]} \n {str(e)}')
        return False

    return True



