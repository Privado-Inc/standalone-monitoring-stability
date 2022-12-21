import os
import shutil
import subprocess
import platform

def main():
    scan_repo_report()

def scan_repo_report():
    repos = get_list_repos()
    cwd = os.getcwd()

    privado_dir = os.path.join(os.path.expanduser('~'), ".privado/bin")

    # create dir if not exist
    if not os.path.isdir(cwd + '/temp/result/stable'):
        os.system('mkdir -p temp/result/stable && mkdir -p temp/result/dev && mkdir -p temp/cpu_mem')

    for repo in repos:         
        scan_dir = cwd + '/temp/repos/' + repo

        # monitor cpu and memory usage
        try:
            if platform.system() == 'Darwin':
                process = subprocess.Popen(["sh", f"{cwd}/utils/cpu_and_memory/cpu_and_memory_usage_mac.sh", repo, "stable"])
            else:
                process = subprocess.Popen(["sh", f"{cwd}/utils/cpu_and_memory/cpu_and_memory_usage.sh", repo, "stable"])
        except:
            print("Unable to fetch CPU and memory Status")
    
        # Scan the cloned repo with stable
        os.system('bash -c "{ time ' + privado_dir + '/privado scan --overwrite --skip-upload ' + scan_dir + ' ; } 2> ' + cwd + '/temp/result/stable/' + repo + '_time.txt" ' )

        # Move the privado.json file to the result folder
        src_path = f'{scan_dir}/.privado/privado.json' 
        dest_path = f'{cwd}/temp/result/stable/{repo}.json'
        shutil.copy(src_path,dest_path)

        # Scan the cloned repo with dev
        os.system('bash -c "{ time PRIVADO_DEV=1 ' + privado_dir + '/privado scan --overwrite --skip-upload ' + scan_dir + ' ; } 2> ' + cwd + '/temp/result/dev/' + repo + '_time.txt" ' )

        dest_path = f'{cwd}/temp/result/dev/{repo}.json'
        # Move the privado.json file to the result folder   
        shutil.copy(src_path, dest_path)

        # kill backgroud running process created for cpu monitoring
        os.system(f"kill -9 {process.pid}")

# Return list of cloned repo name
def get_list_repos():
    result = []
    repos = os.listdir(os.getcwd() + "/temp/repos")
    for repo in repos:
        if not repo.startswith('.'):
            result.append(repo)
    return result

if __name__ == "__main__":
    main()