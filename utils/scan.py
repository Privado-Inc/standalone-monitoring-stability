import os
import subprocess
import shutil

def main():
    scan_repo_report()

def scan_repo_report():
    repos = get_list_repos()
    cwd = os.getcwd()

    print(cwd)

    privado_dir = os.path.join(os.path.expanduser('~'), ".privado/bin")
    scan_dir = cwd + '/repos/' + repos[0]

    # Scan the cloned repo with stable
    os.system(privado_dir + "/privado scan --skip-upload " + scan_dir)

    # Move the privado.json file to the result folder as stable.json
    shutil.move(cwd + '/repos/' + repos[0] + '/.privado/privado.json', cwd + '/result/stable.json')

    # Scan the cloned repo with dev
    os.system('PRIVADO_DEV=1 ' + privado_dir + '/privado scan --overwrite --skip-upload ' + scan_dir)

    # # Move the privado.json file to the result folder as dev.json
    shutil.move(cwd + '/repos/' + repos[0] + '/.privado/privado.json', cwd + '/result/dev.json')

# Return list of cloned repo name
def get_list_repos():
    result = []
    repos = os.listdir("./repos")
    for i in repos:
        if not i.startswith('.'):
            result.append(i)
    return result

if __name__ == "__main__":
    main()