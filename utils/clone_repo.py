import shutil
import datetime
from git.repo.base import Repo
import config
import os

import builder
from utils.helpers import print_timestamp


def clone_repo_with_location(repo_path, location, git_url: bool):
    repo_name = repo_path.split('/')[-1].split('.')[0]
    if git_url:
        clone_repo_with_name(repo_path, location, repo_name)
    else:
        copy_directory(repo_path, location)


def clone_repo_with_name(repo_path, location, name):
    try:
        print_timestamp(f'Cloning {name}')
        repo = Repo.clone_from(repo_path, location)
        print_timestamp(f'Cloned Successfully for {name}')
        return repo
    except Exception as e:
        print_timestamp(f'Error While Cloning {repo_path} : {str(e)}')


def copy_directory(src, dst):
    try:
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
        print_timestamp(f'Directory {src} successfully copied to {dst}')
    except shutil.Error as e:
        print_timestamp(f'Directory not copied. Error: {e}')
    except OSError as e:
        print_timestamp(f'Directory not copied. Error: {e}')



def clone_joern_and_checkout(joern_branch, boost=False):
    if boost:
        return
    try:
        print("In joern build")
        repo = Repo.clone_from(config.PRIVADO_JOERN_URL, builder.get_joern_path(joern_branch))
        print("Repo cloned")
        repo.git.checkout(joern_branch)
        print("Checked out branch")
    except Exception as e:
        print(f"Error while cloning joern: {e}")

def checkIfBranchExist(args):
    joern_head_branch = args.custom_joern_head_branch
    print(" ------ " + joern_head_branch + " ------ ")
    temp_dir = f'{os.getcwd()}/privado-core-temp'
    if os.path.isdir(temp_dir):
        os.system(f'mkdir -r {temp_dir}')
    repo = clone_repo_with_name(f"https://{os.getenv('CORE_AT')}@github.com/Privado-Inc/privado-core-enterprise.git", f'{temp_dir}', "privado-core-enterprise")
    try:
        # Used to check out release tags
        for remote in repo.remotes:
            remote.fetch()
        # fetch all branch info
        repo.remotes.origin.fetch()

        remote_branches = [ref.name for ref in repo.refs if ref.name.startswith('origin/')]

        if (f'origin/{joern_head_branch}' in remote_branches):
            print_timestamp(
                f"$Joern's {joern_head_branch} branch present in privado-core, using privado-core ${joern_head_branch} branch to build image.")
            args.head = joern_head_branch
            os.system(f'rm -r {temp_dir}')
    except Exception as e:
        print_timestamp(f'Error while checking privado-core branch: {e}')