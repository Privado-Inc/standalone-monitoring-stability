import datetime
import os
import shutil
from git import Repo
from utils.clone_repo import clone_repo_with_name
import config


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
        privado_repo = clone_repo_with_name("https://github.com/Privado-Inc/privado", f'{temp_dir}/privado', "privado")

    build_binary_and_move(repo, first_branch, config.BASE_BRANCH_FILE_NAME)
    move_log_rule_file(f'{pwd}/temp/privado-core/log4j2.xml', config.BASE_BRANCH_FILE_NAME)
    build_binary_and_move(repo, second_branch, config.HEAD_BRANCH_FILE_NAME)
    move_log_rule_file(f'{pwd}/temp/privado-core/log4j2.xml', config.HEAD_BRANCH_FILE_NAME)


def build_binary_and_move(repo, branch_name, branch_file_name):
    path = os.getcwd()
    core_dir = f'{path}/temp/privado-core'
    binary_dir = f'{core_dir}/target/universal/stage/*'
    final_dir = f'{path}/temp/binary/{branch_file_name}'

    try:
        repo.git.checkout(branch_name)
        o = repo.remotes.origin
        o.pull()
    except Exception:
        print(f'{datetime.datetime.now()} - branch_name + " doesn\'t exist')
    print(f'{datetime.datetime.now()} - Buliding Privado Binary for {branch_name}')
    os.system("cd " + core_dir + " && sbt clean && sbt stage")
    os.system("mkdir -p " + final_dir)
    os.system("mv " + binary_dir + " " + final_dir)
    print(f'{datetime.datetime.now()} - Build Completed')


def build_binary_and_move_for_joern(branch_name, core_dir):
    path = os.getcwd()
    binary_dir = f'{core_dir}/target/universal/stage/*'
    final_dir = f'{path}/temp/binary/{branch_name}'
    print(f'{datetime.datetime.now()} - Buliding Privado Binary for {branch_name}')
    build_output = os.popen("cd " + core_dir + " && sbt clean && sbt stage").read()

    for line in build_output.split('\n'):
        if '[error]' in line:
            raise Exception('Getting sbt error')

    os.system("mkdir -p " + final_dir)
    os.system("mv " + binary_dir + " " + final_dir)
    print(f'{datetime.datetime.now()} - Build Completed for {branch_name}')
    return True


def checkout_repo(branch_name):
    cwd = os.getcwd()
    repo = Repo(f'{cwd}/temp/privado')
    try:
        repo.git.checkout(branch_name)
        o = repo.remotes.origin
        o.pull()
        print(f'{datetime.datetime.now()} - Privado branch changed to {branch_name}')
    except Exception as e:
        print(f'{datetime.datetime.now()} - {branch_name} + " doesn\'t exist: {e}')


def move_log_rule_file(log_path, branch_file_name):
    pwd = os.getcwd()
    final_path = f'{pwd}/temp/log-rule/{branch_file_name}/log4j2.xml'
    dir_location = f'{pwd}/temp/log-rule/{branch_file_name}'
    if os.path.isfile(dir_location):
        return
    else:
        os.system(f'mkdir -p {dir_location}')
    shutil.copy(log_path, final_path)
    print(f'{datetime.datetime.now()} - privado-core log rule moved')

