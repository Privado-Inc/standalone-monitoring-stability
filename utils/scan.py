import os
import shutil

def main():
    scan_repo_report()

def scan_repo_report():
    repos = get_list_repos()
    cwd = os.getcwd()

    privado_dir = os.path.join(os.path.expanduser('~'), ".privado/bin")

    if not os.path.isdir(cwd + '/temp/result/stable'):
        os.system('mkdir -p temp/result/stable && mkdir -p temp/result/dev')

    for i in repos:

        scan_dir = cwd + '/temp/repos/' + i

        # Scan the cloned repo with stable
        os.system(privado_dir + "/privado scan --skip-upload " + scan_dir)

        # Move the privado.json file to the result folder
        shutil.move(scan_dir + '/.privado/privado.json', cwd + '/temp/result/stable/' + i + '.json')

        # Scan the cloned repo with dev
        os.system('PRIVADO_DEV=1 ' + privado_dir + '/privado scan --overwrite --skip-upload ' + scan_dir)

        # Move the privado.json file to the result folder
        shutil.move(scan_dir + '/.privado/privado.json', cwd + '/temp/result/dev/' + i + '.json')

# Return list of cloned repo name
def get_list_repos():
    result = []
    repos = os.listdir(os.getcwd() + "/temp/repos")
    for i in repos:
        if not i.startswith('.'):
            result.append(i)
    return result

if __name__ == "__main__":
    main()