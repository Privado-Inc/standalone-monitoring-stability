import os
from git import Repo
from utils.clone_repo import clone_repo_with_name

def build(first_branch, second_branch, skip_build = False):
    if skip_build and os.path.exists(f"{os.getcwd()}/temp/binary"):
        return
    pwd = os.getcwd()
    temp_dir = f'{pwd}/temp'
    if not os.path.isdir(f'{temp_dir}/privado-core'):
        repo = clone_repo_with_name("https://github.com/Privado-Inc/privado-core", f'{temp_dir}/privado-core', "privado-core")
    else:
        repo = Repo(f'{temp_dir}/privado-core')

    if not os.path.isdir(f'{temp_dir}/privado'):
        clone_repo_with_name("https://github.com/Privado-Inc/privado", f'{temp_dir}/privado', "privado")
    
    build_binary_and_move(repo, first_branch)
    build_binary_and_move(repo, second_branch)

def build_binary_and_move(repo, branch_name):
    path = os.getcwd()
    core_dir = f'{path}/temp/privado-core'
    binary_dir = f'{core_dir}/target/universal/stage/*'
    final_dir = f'{path}/temp/binary/{branch_name}'

    try:
        repo.git.checkout(branch_name)
        o = repo.remotes.origin
        o.pull()
    except Exception:
        print(branch_name + " doesn't exist")
    print("Buliding Privado Binary for " + branch_name)
    os.system("cd " + core_dir + " && sbt clean && sbt stage")
    os.system("mkdir -p " + final_dir)
    os.system("mv " + binary_dir + " " + final_dir)
    print("Build Completed")