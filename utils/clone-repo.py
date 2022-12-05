from git.repo.base import Repo
import os

def main():
    clone_repo(['https://github.com/saurabh-sudo/BankingSystem-Backend'])
    install_privado()

def install_privado():
    print("Please make sure you have Docker install locally.")
    print("Getting the latest image of Privado...")
    path = os.path.join(os.path.expanduser('~'), ".privado/bin")
    if os.path.isdir(path):
        print("Already Have Privado.")
    else:
        os.system("curl -o- https://raw.githubusercontent.com/Privado-Inc/privado-cli/main/install.sh | bash")

def clone_repo(urls):

    for url in urls:
        repo_name = url.split("/")[-1]
        location = "./temp/repos/" + repo_name
        print("Cloning the Repo: " + repo_name)
        Repo.clone_from(url, location)
        print("Cloning Successful: " + repo_name)
    
    print("All repos cloned.")

if __name__ == "__main__":
    main()