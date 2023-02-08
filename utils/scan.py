import os
import shutil
import subprocess
import platform
from utils.write_to_file import write_scan_status_report, create_new_excel, create_new_excel_for_file
import re


def get_docker_commands(tag, repo_path):
    if tag == 'main':
        return f'privado scan {repo_path}'
    elif tag == 'dev':
        return f'PRIVADO_DEV=1 privado scan {repo_path}'
    else:
        return f'PRIVADO_DEV=1 PRIVADO_TAG={tag} privado scan {repo_path}'


def scan_repo_report(first_branch, second_branch, valid_repos, use_docker):
    cwd = os.getcwd()

    # To store scan status - if it failed or completed, and for which branch
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
                first_command = f'cd {cwd}/temp/binary/{first_branch}/bin && ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload -Dlog4j.configurationFile=log4j2.xml | tee {cwd}/temp/result/{first_branch}/{repo}-output.txt'
            
            # Execute the command to generate the binary file for first branch
            os.system(first_command)

            src_path = f'{scan_dir}/.privado/privado.json'
            dest_path = f'{cwd}/temp/result/{first_branch}/{repo}.json'

            report = {}

            # Move the privado.json file to the result folder
            try:
                raise 'error missing'
                shutil.move(src_path, dest_path)
                report[first_branch] = {'scan_status': 'done', 'scan_error_message': '--'}
                # scan_status[f"{repo},{first_branch}"] = "done"
            except Exception as e:
                report[first_branch] = {'scan_status': 'failed', 'scan_error_message': str(e)}
                # scan_status[f"{repo},{first_branch}"] = f'failed,{str(e)}'

            # Scan the cloned repo with second branch and push output to a file with debug logs
            if use_docker:
                second_command = f'{get_docker_commands(second_branch, scan_dir)} | tee {cwd}/temp/result/{second_branch}/{repo}-output.txt'
            else:
                second_command = f'cd {cwd}/temp/binary/{second_branch}/bin && ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload -Dlog4j.configurationFile=log4j2.xml | tee {cwd}/temp/result/{second_branch}/{repo}-output.txt'
            
            # Execute the command to generate the binary file for second branch
            os.system(second_command)

            dest_path = f'{cwd}/temp/result/{second_branch}/{repo}.json'   
            try:
                shutil.move(src_path, dest_path)
                report[second_branch] = {'scan_status': 'done', 'scan_error_message': '--'}
                # scan_status[f"{repo},{second_branch}"] = "done"
            except Exception as e:
                report[second_branch] = {'scan_status': 'failed', 'scan_error_message': str(e)}
                # scan_status[f"{repo},{second_branch}"] = f"failed,{str(e)}"

            scan_report[repo] = report

        finally:
            # Generate and status and export into result
            generate_scan_status_data(scan_report, first_branch, second_branch)
            # write_scan_status_report(f'{cwd}/output.xlsx', scan_status_report_data)

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
    scan_status_report_data = [[
        "Repo", "Branch", "scan status", "scan error", "comparison status", "comparison error", "unique flow count", "scan time", "CPG size"
    ]]
    cwd = os.getcwd()

    # create the empty excel file
    create_new_excel(f"{cwd}/output.xlsx", first_branch, second_branch)

    for repo in scan_report.keys():
        parse_flows_data(repo, first_branch, scan_report)
        parse_flows_data(repo, second_branch, scan_report)

    # for repo_branch, status in scan_status.items():
    #     repo, branch = repo_branch.split(',')
    #     status_breakdown = status.split(',')
    #     error_message = "--"
    #
    #     scan_metadata_regex = r".*(Code scanning|Binary file size|Deduplicating flows is done in).*"
    #     scan_metadata_values = []
    #
    #     with open(f"{cwd}/temp/result/{branch.strip()}/{repo}-output.txt") as scan_time_output:
    #         for line in scan_time_output.readlines():
    #             if re.search(scan_metadata_regex, line):
    #                 scan_metadata_values.append(line)
    #
    #     unique_flows = ""
    #     code_scan_time = ""
    #     binary_file_size = ""
    #
    #     try:
    #         unique_flows = scan_metadata_values[0].split('-')[-1]
    #         code_scan_time = scan_metadata_values[1].split('-')[-2]
    #         binary_file_size = scan_metadata_values[2].split('-')[-1]
    #     except Exception as e:
    #         print(f'Error during parsing the status data: {e}')
    #
    #     if len(status_breakdown) > 1:
    #         error_message = status_breakdown[1]
    #
    #     comparison_status = "failed" if len(status_breakdown) > 1 else "done"
    #     scan_status_report_data.append([repo, branch, status_breakdown[0], error_message, comparison_status, "--", unique_flows, code_scan_time, binary_file_size])
    #
    # scan_status_report_data.append([])
    # return scan_status_report_data

def parse_flows_data(repo_name, branch_name, scan_report):

    cwd = os.getcwd()

    scan_metadata_regex = r".*(Code scanning|Binary file size|Deduplicating flows is done in).*"
    scan_metadata_values = []

    with open(f"{cwd}/temp/result/{branch_name}/{repo_name}-output.txt") as scan_time_output:
        for line in scan_time_output.readlines():
            if re.search(scan_metadata_regex, line):
                scan_metadata_values.append(line)

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
        print(f'Error while parsing code scan time data: {e}')
        scan_report[repo_name][branch_name]['code_scan_time'] = '--'

    try:
        binary_file_size = scan_metadata_values[2].split('-')[-1]
        scan_report[repo_name][branch_name]['binary_file_size'] = binary_file_size
    except Exception as e:
        print(f'Error while parsing binary file size data: {e}')
        scan_report[repo_name][branch_name]['binary_file_size'] = '--'
