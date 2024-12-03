import os
import shutil
import datetime

import builder
from utils.helpers import print_timestamp
from utils.processor.stage_metadata import get_summary_extract, update_diff_cache
from utils.write_to_file import write_scan_status_report, create_new_excel, create_new_excel_for_file, \
    write_to_action_result
import re
import config


def get_detected_language(repo, branch):
    cwd = os.getcwd()
    with open(f'{cwd}/temp/result/{branch}/{repo}-output.txt') as scan_time_output:
        for line in scan_time_output.readlines():
            if re.search(r".*(Detected language).*", line):
                detected_language = line.split(' ')[-1].replace("'", "")
                return detected_language


def get_docker_commands(tag, repo_path):
    if tag == 'main':
        return f'privado  {repo_path}'
    elif tag == 'dev':
        return f'PRIVADO_DEV=1 privado  {repo_path}'
    else:
        return f'PRIVADO_DEV=1 PRIVADO_TAG={tag} privado  {repo_path}'


def scan_repo_report(valid_repos, args):
    cwd = os.getcwd()

    # To store  status - if it failed or completed, and for which branch
    scan_report = dict()
    #
    # rules_branches = get_rules_branch(first_branch, second_branch, rules_branch_base, rules_branch_head)
    # create dirs for results if not exist
    if not os.path.isdir(cwd + '/temp/result/' + config.BASE_CORE_BRANCH_KEY):
        os.system('mkdir -p ' + cwd + '/temp/result/' + config.BASE_CORE_BRANCH_KEY)
    if not os.path.isdir(cwd + '/temp/result/' + config.HEAD_CORE_BRANCH_KEY):
        os.system('mkdir -p ' + cwd + '/temp/result/' + config.HEAD_CORE_BRANCH_KEY)

    for repo in valid_repos:
        scan_dir = cwd + '/temp/repos/' + repo
        try:
            # Scan the cloned repo with first branch and push output to a file
            first_command = build_command(cwd, config.BASE_CORE_BRANCH_NAME, config.BASE_CORE_BRANCH_KEY, scan_dir,
                                          repo, args.generate_unique_flow, args.debug_mode,
                                          args.use_docker)

            print(f"first command {first_command}")

            # Execute the command to generate the binary file for first branch
            os.system(first_command)

            src_path = f'{scan_dir}/.privado/privado.json'
            dest_path = f'{cwd}/temp/result/{config.BASE_CORE_BRANCH_KEY}/{repo}.json'

            src_path_semantic = f'{scan_dir}/.privado/semantic.txt'
            dest_path_semantic = f'{cwd}/temp/result/{config.BASE_CORE_BRANCH_KEY}/{repo}-semantic.txt'

            src_path_intermediate = f'{scan_dir}/.privado/intermediate.json'
            dest_path_intermediate = f'{cwd}/temp/result/{config.BASE_CORE_BRANCH_KEY}/{repo}-intermediate.json'

            src_path_stage_metadata = f'{scan_dir}/.privado/stageMetadata.json'
            dest_path_stage_metadata = f'{cwd}/temp/result/{config.BASE_CORE_BRANCH_KEY}/{repo}-stageMetadata.json'

            base_stage_metadata = None
            head_stage_metadata = None
            if os.path.isfile(src_path_semantic):
                shutil.move(src_path_semantic, dest_path_semantic)

            if os.path.isfile(src_path_intermediate):
                shutil.move(src_path_intermediate, dest_path_intermediate)

            if os.path.isfile(src_path_stage_metadata):
                shutil.move(src_path_stage_metadata, dest_path_stage_metadata)
                base_stage_metadata = get_summary_extract(dest_path_stage_metadata)
            report = {}

            # Move the privado.json file to the result folder
            try:
                shutil.move(src_path, dest_path)
                report[config.BASE_CORE_BRANCH_KEY] = {'scan_status': 'done', 'scan_error_message': '--'}
            except Exception as e:
                report[config.BASE_CORE_BRANCH_KEY] = {'scan_status': 'failed', 'scan_error_message': str(e)}
                write_to_action_result(f"{repo} - scan failed\n")

            # Scan the cloned repo with second branch and push output to a file with debug logs
            second_command = build_command(cwd, config.HEAD_CORE_BRANCH_NAME, config.HEAD_CORE_BRANCH_KEY, scan_dir,
                                           repo, args.generate_unique_flow, args.debug_mode, args.use_docker)

            print(second_command)
            language = get_detected_language(repo, config.BASE_CORE_BRANCH_KEY)
            report["language"] = language

            # Execute the command to generate the binary file for second branch
            os.system(second_command)

            dest_path = f'{cwd}/temp/result/{config.HEAD_CORE_BRANCH_KEY}/{repo}.json'
            dest_path_intermediate = f'{cwd}/temp/result/{config.HEAD_CORE_BRANCH_KEY}/{repo}-intermediate.json'
            dest_path_semantic = f'{cwd}/temp/result/{config.HEAD_CORE_BRANCH_KEY}/{repo}-semantic.txt'
            dest_path_stage_metadata = f'{cwd}/temp/result/{config.HEAD_CORE_BRANCH_KEY}/{repo}-stageMetadata.json'

            # move the intermediate result if exist
            if os.path.isfile(src_path_intermediate):
                shutil.move(src_path_intermediate, dest_path_intermediate)

            if os.path.isfile(src_path_stage_metadata):
                shutil.move(src_path_stage_metadata, dest_path_stage_metadata)
                head_stage_metadata = get_summary_extract(dest_path_stage_metadata)

            update_diff_cache(base_stage_metadata, head_stage_metadata)
            try:
                shutil.move(src_path, dest_path)
                report[config.HEAD_CORE_BRANCH_KEY] = {'scan_status': 'done', 'scan_error_message': '--'}
            except Exception as e:
                report[config.HEAD_CORE_BRANCH_KEY] = {'scan_status': 'failed', 'scan_error_message': str(e)}
                write_to_action_result(f"{repo} - scan failed\n")
            
            scan_report[repo] = report

        finally:
            pass
   
    generate_scan_status_data(scan_report)
    return scan_report


# Return list of cloned repo name stored in /temp/repos dir
def get_list_repos():
    result = []
    repos = os.listdir(os.getcwd() + "/temp/repos")
    for repo in repos:
        if not repo.startswith('.'):
            result.append(repo)
    return result


def generate_scan_status_data_for_file(repo_name, first_file, second_file):
    scan_status_report_data = [['First File', first_file], ['Second File', second_file], ['Repo', repo_name]]
    cwd = os.getcwd()
    create_new_excel_for_file(f"{cwd}/output.xlsx", first_file, second_file)
    return scan_status_report_data


def generate_scan_status_data(scan_report):
    cwd = os.getcwd()

    # create the empty Excel file
    create_new_excel(f"{cwd}/output.xlsx", config.BASE_SHEET_BRANCH_NAME.replace('/', '-'),
                     config.HEAD_SHEET_BRANCH_NAME.replace('/', '-'))

    for repo in scan_report.keys():
        parse_flows_data(repo, config.BASE_CORE_BRANCH_NAME, config.BASE_CORE_BRANCH_KEY, scan_report)
        parse_flows_data(repo, config.HEAD_CORE_BRANCH_NAME, config.HEAD_CORE_BRANCH_KEY, scan_report)


def parse_flows_data(repo_name, branch_name, branch_key, scan_report):

    cwd = os.getcwd()

    source_regex = r".*(no of source nodes).*"
    final_flows_regex = r".*(Processed final flows).*"
    scan_metadata_values = []
    source_metadata_values = []

    with open(f"{cwd}/temp/result/{branch_key}/{repo_name}-output.txt") as scan_time_output:
        for line in scan_time_output.readlines():
            if re.search(source_regex, line):
                source_metadata_values.append(line)
            if re.search(final_flows_regex, line):
                scan_metadata_values.append(line)

    try:
        unique_flows = scan_metadata_values[0].split('-')[-1]
        scan_report[repo_name][branch_key]['unique_flows'] = unique_flows
    except Exception as e:
        print_timestamp(f'Error while parsing unique flow data: {e}')
        scan_report[repo_name][branch_key]['unique_flows'] = '--'

    try:
        source_count = source_metadata_values[0].split()[-1]
        scan_report[repo_name][branch_key]['unique_source'] = source_count
    except Exception as e:
        print_timestamp(f'Error while parsing unique source data: {e}')
        scan_report[repo_name][branch_key]['unique_source'] = '--'


# Build the scan command
def build_command(cwd, branch_name, key, scan_dir, repo, unique_flow, debug_mode, use_docker):
    if use_docker:
        return f'{get_docker_commands(branch_name, scan_dir)} | tee {cwd}/temp/result/{key}/{repo}-output.txt'

    command = [f'export _JAVA_OPTIONS="-Xmx14G" && cd {cwd}/temp/binary/{key}/bin && ./privado-core scan', scan_dir,
               f'-ic {cwd}/temp/privado/{key} --skip-upload']

    if unique_flow:
        command.append('--test-output')
    if debug_mode:
        command.append(f'-Dlog4j.configurationFile={cwd}/temp/log-rule/{key}/log4j2.xml')
    command.append(f'2>&1 | tee -a {cwd}/temp/result/{key}/{repo}-output.txt')

    return ' '.join(command)
