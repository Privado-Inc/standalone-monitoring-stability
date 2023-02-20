import os
import shutil
import subprocess
import platform
from utils.write_to_file import write_scan_status_report, create_new_excel, create_new_excel_for_file
import re

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


def scan_repo_report(first_branch, second_branch, valid_repos, use_docker, generate_unique_flow):
    cwd = os.getcwd()

    # To store  status - if it failed or completed, and for which branch
    scan_report = dict()

    # create dirs for results if not exist
    if not os.path.isdir(cwd + '/temp/result/' + first_branch):
        os.system('mkdir -p ' + cwd + '/temp/result/' + first_branch)
    if not os.path.isdir(cwd + '/temp/result/' + second_branch):
        os.system('mkdir -p ' + cwd + '/temp/result/' + second_branch)

    for repo in valid_repos:
        scan_dir = cwd + '/temp/repos/' + repo
        try:
            # Scan the cloned repo with first branch and push output to a file
            if use_docker:
                first_command = f'{get_docker_commands(first_branch, scan_dir)} | tee {cwd}/temp/result/{first_branch}/{repo}-output.txt'
            else:
                if generate_unique_flow:
                    first_command = f'cd {cwd}/temp/binary/{first_branch}/bin && ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload --test-output -Dlog4j.configurationFile=log4j2.xml | tee {cwd}/temp/result/{first_branch}/{repo}-output.txt'
                else:
                    first_command = f'cd {cwd}/temp/binary/{first_branch}/bin && ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload -Dlog4j.configurationFile=log4j2.xml | tee {cwd}/temp/result/{first_branch}/{repo}-output.txt'
            
            # Execute the command to generate the binary file for first branch
            os.system(first_command)

            src_path = f'{scan_dir}/.privado/privado.json'
            dest_path = f'{cwd}/temp/result/{first_branch}/{repo}.json'

            src_path_intermediate = f'{scan_dir}/.privado/intermediate.json'
            dest_path_intermediate = f'{cwd}/temp/result/{first_branch}/{repo}-intermediate.json'

            if os.path.isfile(src_path_intermediate):
                shutil.move(src_path_intermediate, dest_path_intermediate)

            report = {}

            # Move the privado.json file to the result folder
            try:
                shutil.move(src_path, dest_path)
                report[first_branch] = {'scan_status': 'done', 'scan_error_message': '--'}
            except Exception as e:
                report[first_branch] = {'scan_status': 'failed', 'scan_error_message': str(e)}

            # Scan the cloned repo with second branch and push output to a file with debug logs
            if use_docker:
                second_command = f'{get_docker_commands(second_branch, scan_dir)} | tee {cwd}/temp/result/{second_branch}/{repo}-output.txt'
            else:
                if generate_unique_flow:
                    second_command = f'cd {cwd}/temp/binary/{second_branch}/bin && ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload --test-output -Dlog4j.configurationFile=log4j2.xml | tee {cwd}/temp/result/{second_branch}/{repo}-output.txt'
                else:
                    second_command = f'cd {cwd}/temp/binary/{second_branch}/bin && ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload -Dlog4j.configurationFile=log4j2.xml | tee {cwd}/temp/result/{second_branch}/{repo}-output.txt'
            
            language = get_detected_language(repo, first_branch)
            report["language"] = language
            # Execute the command to generate the binary file for second branch
            os.system(second_command)

            dest_path = f'{cwd}/temp/result/{second_branch}/{repo}.json'
            dest_path_intermediate = f'{cwd}/temp/result/{second_branch}/{repo}-intermediate.json'

            # move the intermediate result if exist
            if os.path.isfile(src_path_intermediate):
                shutil.move(src_path_intermediate, dest_path_intermediate)

            try:
                shutil.move(src_path, dest_path)
                report[second_branch] = {'scan_status': 'done', 'scan_error_message': '--'}
            except Exception as e:
                report[second_branch] = {'scan_status': 'failed', 'scan_error_message': str(e)}
            
            scan_report[repo] = report

        finally:
            # Generate and status and export into result
            generate_scan_status_data(scan_report, first_branch, second_branch)

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


def generate_scan_status_data(scan_report, first_branch, second_branch):
    cwd = os.getcwd()

    # create the empty excel file
    create_new_excel(f"{cwd}/output.xlsx", first_branch.replace('/', '-'), second_branch.replace('/', '-'))

    for repo in scan_report.keys():
        parse_flows_data(repo, first_branch, scan_report)
        parse_flows_data(repo, second_branch, scan_report)


def parse_flows_data(repo_name, branch_name, scan_report):

    cwd = os.getcwd()

    scan_metadata_regex = r".*(Code scanning|Binary file size|Deduplicating flows is done in).*"
    source_regex = r".*(no of source nodes).*"
    reachable_by_flow_regex = r".*(Finding flows is done in).*"
    scan_metadata_values = []
    source_metadata_values = []
    reachable_by_flow_values = []

    with open(f"{cwd}/temp/result/{branch_name}/{repo_name}-output.txt") as scan_time_output:
        for line in scan_time_output.readlines():
            if re.search(scan_metadata_regex, line):
                scan_metadata_values.append(line)
            if re.search(source_regex, line):
                source_metadata_values.append(line)
            if re.search(reachable_by_flow_regex, line):
                reachable_by_flow_values.append(line)

    try:
        unique_flows = scan_metadata_values[0].split('-')[-1]
        scan_report[repo_name][branch_name]['unique_flows'] = unique_flows
    except Exception as e:
        print(f'Error while parsing unique flow data: {e}')
        scan_report[repo_name][branch_name]['unique_flows'] = '--'

    try:
        code_scan_time = scan_metadata_values[1].split('-')[-2]
        scan_report[repo_name][branch_name]['code_scan_time'] = code_scan_time
    except Exception as e:
        print(f'Error while parsing code  time data: {e}')
        scan_report[repo_name][branch_name]['code_scan_time'] = '--'

    try:
        binary_file_size = scan_metadata_values[2].split('-')[-1]
        scan_report[repo_name][branch_name]['binary_file_size'] = binary_file_size
    except Exception as e:
        print(f'Error while parsing binary file size data: {e}')
        scan_report[repo_name][branch_name]['binary_file_size'] = '--'

    try:
        source_count = source_metadata_values[0].split()[-1]
        scan_report[repo_name][branch_name]['unique_source'] = source_count
    except Exception as e:
        print(f'Error while parsing unique source data: {e}')
        scan_report[repo_name][branch_name]['unique_source'] = '--'

    try:
        reachable_by_flow_time = reachable_by_flow_values[0].split('ms')[0].split('-')[-1]
        scan_report[repo_name][branch_name]['reachable_flow_time'] = reachable_by_flow_time
    except Exception as e:
        print(f'Error while parsing reachable flow time data: {e}')
        scan_report[repo_name][branch_name]['reachable_flow_time'] = '--'
