import os
import shutil
import subprocess
import platform
from utils.write_to_file import write_scan_status_report


def scan_repo_report(first_branch, second_branch):
    repos = get_list_repos()
    cwd = os.getcwd()

    scan_status = dict() # To store scan status - if it failed or completed, and for which branch 
    

    # create dirs for results if not exist
    if not os.path.isdir(cwd + '/temp/result/' + first_branch): os.system('mkdir -p ' + cwd + '/temp/result/' + first_branch)
    if not os.path.isdir(cwd + '/temp/result/' + second_branch): os.system('mkdir -p ' + cwd + '/temp/result/' + second_branch)  
    if not os.path.isdir(cwd + '/temp/cpu_mem'): os.system('mkdir -p ' + cwd + '/temp/cpu_mem')

    for repo in repos:         
        scan_dir = cwd + '/temp/repos/' + repo

        # monitor cpu and memory usage
        try:
            try:
                # monitor cpu and memory usage
                # For mac devices
                if platform.system() == 'Darwin': 
                    process = subprocess.Popen(["sh", f"{cwd}/utils/cpu_and_memory/cpu_and_memory_usage_mac.sh", repo, "stable"])
                else:
                    process = subprocess.Popen(["sh", f"{cwd}/utils/cpu_and_memory/cpu_and_memory_usage.sh", repo, "stable"])
            except:
                print("Unable to fetch CPU and memory Status")
    
            # Scan the cloned repo with first branch and push output to a file
            first_command = f'cd {cwd}/temp/binary/{first_branch}/bin && ({{ time ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload -Dlog4j.configurationFile=log4j2.xml ; }} 2> {cwd}/temp/result/{first_branch}/{repo}_time.txt | tee {cwd}/temp/result/{first_branch}/{repo}-output.txt)'
            # Execute the command to generate the binary file for first branch
            os.system(first_command)



            # Move the privado.json file to the result folder
            src_path = f'{scan_dir}/.privado/privado.json'

            # if (os.path.exists(scan_dir)): # If privado.json is generated, the scan is successful
            #     scan_status[f"{repo}-{first_branch}"] = "done"
            # else:
            #     scan_status[f"{repo}-{first_branch}"] = "failed"

            dest_path = f'{cwd}/temp/result/{first_branch}/{repo}.json'
            try:
                shutil.move(src_path,dest_path)
                scan_status[f"{repo},{first_branch}"] = "done"
            except:
                scan_status[f"{repo},{first_branch}"] = "failed"


            # Scan the cloned repo with second branch and push output to a file with debug logs
            second_command = f'cd {cwd}/temp/binary/{second_branch}/bin && ({{ time ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload -Dlog4j.configurationFile=log4j2.xml ; }} 2> {cwd}/temp/result/{second_branch}/{repo}_time.txt | tee {cwd}/temp/result/{second_branch}/{repo}-output.txt)'
            # Execute the command to generate the binary file for second branch
            os.system(second_command)
            
            # if (os.path.exists(scan_dir)): # If privado.json is generated, the scan is successful
            #     scan_status[f"{repo}-{first_branch}"] = "done"
            # else:
            #     scan_status[f"{repo}-{first_branch}"] = "failed"
            # Move the privado.json file to the result folder
            dest_path = f'{cwd}/temp/result/{second_branch}/{repo}.json'   
            try:
                shutil.move(src_path,dest_path)
                scan_status[f"{repo},{second_branch}"] = "done"
            except Exception(e):
                scan_status[f"{repo},{second_branch}"] = f"failed,{str(e)}"

        finally:
            scan_status_report_data = generate_scan_status_data(scan_status, first_branch, second_branch)
            write_scan_status_report(f'{cwd}/output.xlsx', scan_status_report_data, first_branch, second_branch)

            # kill backgroud running process created for cpu monitoring
            os.system(f"kill -9 {process.pid}")

# Return list of cloned repo name stored in /temp/repos dir
def get_list_repos():
    result = []
    repos = os.listdir(os.getcwd() + "/temp/repos")
    for repo in repos:
        if not repo.startswith('.'):
            result.append(repo)
    return result



def generate_scan_status_data(scan_status, first_branch, second_branch):
    scan_status_report_data = [[
        "Repo", "Branch", "scan status", "scan error", "comparison status", "comparison error", "unique flow", "count", "scan time", "CPG size"
    ]]
    
    for repo_branch, status in scan_status.items():
        print(repo_branch)
        print(status)
        repo, branch = repo_branch.split(',')
        status_breakdown = status.split(',')
        error_message = "--"

        scan_metadata_regex = r".*(code scanning|binary file size|Deduplicating flows is done in).*"
        scan_metadata_values = []

        with open(f"{cwd}/temp/result/{first_branch}/output.txt") as scan_time_output:
            for line in scan_time_output.readlines():
                if (re.search(scan_metadata_regex, line)):
                    scan_metadata_values.push(line)

        with open(f"{cwd}/temp/result/{second_branch}output.txt") as scan_time_output:
            for line in scan_time_output.readlines():
                if (re.search(scan_metadata_regex, line)):
                    scan_metadata_values.push(line)

        try:
            unique_flows = scan_metadata_values[0].split('-')[-1] 
            code_scan_time = scan_metadata_values[1].split('-')[-2]
            binary_file_size = scan_metadata_values[2].split('-')[-1]
        except:
            print("Something went wrong")
            


        if (len(status_breakdown) > 1):
            error_message = status_breakdown[1]

        comparison_status = "done" if len(status_breakdown) > 1 else "failed"
        scan_status_report_data.append([repo, branch, status_breakdown[0], error_message, comparison_status, "--", unique_flows, code_scan_time, binary_file_size])
    
    return scan_status_report_data

