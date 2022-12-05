import os
import subprocess

def main():
    scan_repo_report()

def scan_repo_report():
    repos = get_list_repos()

    for i in repos:
        privado_dir = os.path.join(os.path.expanduser('~'), ".privado/bin/privado")
        scan_dir = './repos/' + i
        print(privado_dir + " scan --skip-upload " + scan_dir)
        os.system(privado_dir + " scan --skip-upload " + scan_dir)

# Return list of cloned repo name
def get_list_repos():
    repos = os.listdir("./repos")
    return repos

if __name__ == "__main__":
    main()