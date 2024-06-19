import shutil
import datetime
from git.repo.base import Repo
import config

import builder


def clone_repo_with_location(repo_path, location, git_url: bool):
    repo_name = repo_path.split('/')[-1].split('.')[0]
    if git_url:
        clone_repo_with_name(repo_path, location, repo_name)
    else:
        copy_directory(repo_path, location)


def clone_repo_with_name(repo_path, location, name):
    try:
        print(f'{builder.get_current_time()} - Cloning {name}')
        repo = Repo.clone_from(repo_path, location)
        print(f'{builder.get_current_time()} - Cloned Successfully for {name}')
        return repo
    except Exception as e:
        print(f'{builder.get_current_time()} - Error While Cloning {repo_path} : {str(e)}')


def copy_directory(src, dst):
    try:
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
        print(f'{builder.get_current_time()} - Directory {src} successfully copied to {dst}')
    except shutil.Error as e:
        print(f'{builder.get_current_time()} - Directory not copied. Error: {e}')
    except OSError as e:
        print(f'{builder.get_current_time()} - Directory not copied. Error: {e}')



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