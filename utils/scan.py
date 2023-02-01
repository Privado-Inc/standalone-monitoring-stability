import os
import shutil
import subprocess
import platform

def scan_repo_report(first_branch, second_branch):
    repos = get_list_repos()
    cwd = os.getcwd()

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
            dest_path = f'{cwd}/temp/result/{first_branch}/{repo}.json'
            shutil.move(src_path,dest_path)

            # Scan the cloned repo with second branch and push output to a file with debug logs
            second_command = f'cd {cwd}/temp/binary/{second_branch}/bin && ({{ time ./privado-core scan {scan_dir} -ic {cwd}/temp/privado --skip-upload -Dlog4j.configurationFile=log4j2.xml ; }} 2> {cwd}/temp/result/{second_branch}/{repo}_time.txt | tee {cwd}/temp/result/{second_branch}/{repo}-output.txt)'
            # Execute the command to generate the binary file for seconf branch
            os.system(second_command)
            
            # Move the privado.json file to the result folder
            dest_path = f'{cwd}/temp/result/{second_branch}/{repo}.json'   
            shutil.move(src_path, dest_path)
        finally:
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