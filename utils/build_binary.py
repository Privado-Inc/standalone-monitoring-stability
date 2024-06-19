import os
import shutil

import builder
from utils.clone_repo import clone_repo_with_name
import config
import re

def read_joern_version_from_file(filePath="./temp/m2Version.txt"):
    with open(filePath, "r") as f:
        return f"{f.read().strip()}"     

def change_joern_in_build_file(repo_path, joern_branch):
    version = read_joern_version_from_file(f"./temp/m2Version_{joern_branch}.txt").strip()
    joernVersionRegex = "val joernVersion([ ]*)= .*"
    print(f"Old version: {joernVersionRegex}")
    updatedJoernVersion  = f"val joernVersion = \"{version}\""
    print(f"New version: {updatedJoernVersion}")
    print("Updating joern version....")
    updated_build_file = ""
    with open(f"{repo_path}/build.sbt", "r") as f:
        updated_build_file = re.sub(joernVersionRegex, updatedJoernVersion,f.read())

    with open(f"{repo_path}/build.sbt", "w") as f:
        f.write(updated_build_file)



def build(skip_build = False, custom_joern = False, joern_base=None, joern_head=None):
    print(f"Building binary for privado-core with custom joern: {custom_joern}")
    if skip_build and os.path.exists(f"{os.getcwd()}/temp/binary"):
        return
    pwd = os.getcwd()
    temp_dir = f'{pwd}/temp'

    base_core_repo_path = f'{temp_dir}/privado-core/{config.BASE_CORE_BRANCH_KEY}'
    head_core_repo_path = f'{temp_dir}/privado-core/{config.HEAD_CORE_BRANCH_KEY}'
    base_rule_repo_path = f'{temp_dir}/privado/{config.BASE_CORE_BRANCH_KEY}'
    head_rule_repo_path = f'{temp_dir}/privado/{config.HEAD_CORE_BRANCH_KEY}'

    if not os.path.isdir(base_core_repo_path):
        clone_privado_core_repo(config.BASE_PRIVADO_CORE_URL, config.BASE_CORE_BRANCH_NAME, base_core_repo_path,
                                f'{config.BASE_PRIVADO_CORE_OWNER}-{config.BASE_CORE_BRANCH_NAME}')
        
        if (custom_joern):
            change_joern_in_build_file(base_core_repo_path, joern_base)


    if not os.path.isdir(head_core_repo_path):
        clone_privado_core_repo(config.HEAD_PRIVADO_CORE_URL, config.HEAD_CORE_BRANCH_NAME,
                                head_core_repo_path, f'{config.HEAD_PRIVADO_CORE_OWNER}-{config.HEAD_CORE_BRANCH_NAME}')
        if custom_joern:
            change_joern_in_build_file(head_core_repo_path, joern_head)

    if not os.path.isdir(base_rule_repo_path):
        clone_privado_core_repo(config.BASE_PRIVADO_RULE_URL, config.BASE_RULE_BRANCH_NAME, base_rule_repo_path,
                                f'{config.BASE_PRIVADO_RULE_OWNER}-{config.BASE_RULE_BRANCH_NAME}')

    if not os.path.isdir(head_rule_repo_path):
        clone_privado_core_repo(config.HEAD_PRIVADO_RULE_URL, config.HEAD_RULE_BRANCH_NAME, head_rule_repo_path,
                                f'{config.HEAD_PRIVADO_RULE_OWNER}-{config.HEAD_RULE_BRANCH_NAME}')
    build_binary_and_move("privado-core", config.BASE_CORE_BRANCH_KEY)
    move_log_rule_file(f'{pwd}/temp/privado-core/{config.BASE_CORE_BRANCH_KEY}/log4j2.xml', config.BASE_CORE_BRANCH_KEY)
    build_binary_and_move("privado-core", config.HEAD_CORE_BRANCH_KEY)
    move_log_rule_file(f'{pwd}/temp/privado-core/{config.HEAD_CORE_BRANCH_KEY}/log4j2.xml', config.HEAD_CORE_BRANCH_KEY)


def build_binary_and_move(repo_name, key):
    path = os.getcwd()
    core_dir = f'{path}/temp/{repo_name}/{key}'
    binary_dir = f'{core_dir}/target/universal/stage/*'
    final_dir = f'{path}/temp/binary/{key}'

    print(f'{builder.get_current_time()} - Buliding Privado Binary for {key}')
    os.system("cd " + core_dir + " && sbt clean && sbt stage")
    os.system("mkdir -p " + final_dir)
    os.system("mv " + binary_dir + " " + final_dir)
    print(f'{builder.get_current_time()} - Build Completed')


def build_binary_and_move_for_joern(core_dir, key):
    path = os.getcwd()
    binary_dir = f'{core_dir}/target/universal/stage/*'
    final_dir = f'{path}/temp/binary/{key}'
    print(f'{builder.get_current_time()} - Buliding Privado Binary for {key}')
    build_output = os.popen("cd " + core_dir + " && sbt clean && sbt stage").read()

    for line in build_output.split('\n'):
        if '[error]' in line:
            raise Exception('Getting sbt error')

    os.system("mkdir -p " + final_dir)
    os.system("mv " + binary_dir + " " + final_dir)
    print(f'{builder.get_current_time()} - Build Completed')
    return True


def move_log_rule_file(log_path, key):
    pwd = os.getcwd()
    final_path = f'{pwd}/temp/log-rule/{key}/log4j2.xml'
    dir_location = f'{pwd}/temp/log-rule/{key}'
    if os.path.isfile(dir_location):
        return
    else:
        os.system(f'mkdir -p {dir_location}')
    shutil.copy(log_path, final_path)
    print(f'{builder.get_current_time()} - privado-core log rule moved')


def clone_privado_core_repo(repo_url, branch_name, temp_dir, name):
    repo = clone_repo_with_name(repo_url, f'{temp_dir}', name)
    try:
        repo.git.checkout(branch_name)
        o = repo.remotes.origin
        o.pull()
        print(f'{builder.get_current_time()} - Privado branch changed to {branch_name}')
    except Exception as e:
        print(f'{builder.get_current_time()} - {branch_name} + " doesn\'t exist: {e}')


def publish_joern_and_get_version(branch_name):
    print(f"In publish for branch: {branch_name}")
    awk_split = "awk '{split($0,a,\"/\"); print a[9]}'"
    os.system(f"cd {os.getcwd()}/temp/joern_{branch_name} && sbt publishM2 | grep published | {awk_split} | sort -u > ../m2Version_{branch_name}.txt")