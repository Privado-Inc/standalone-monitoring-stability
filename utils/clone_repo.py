import shutil
from git.repo.base import Repo

def clone_repo_with_location(repo_path, location, git_url: bool):
    repo_name = repo_path.split('/')[-1].split('.')[0]
    print(repo_name)
    if git_url:
        clone_repo_with_name(repo_path, location, repo_name)
    else:
        copy_directory(repo_path, location)

def clone_repo_with_name(repo_path, location, name):
    try:
        print("Cloning " + name)
        repo = Repo.clone_from(repo_path, location)
        print("Cloned Successfully")
        return repo
    except Exception:
        print("Error While Cloning " + repo_path)

def copy_directory(src, dst):
    try:
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
        print(f"Directory {src} successfully copied to {dst}")
    except shutil.Error as e:
        print(f"Directory not copied. Error: {e}")
    except OSError as e:
        print(f"Directory not copied. Error: {e}")

