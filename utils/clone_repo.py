from git.repo.base import Repo

def clone_repo_with_location(repo_path, location):
    repo_name = repo_path.split('/')[-1].split('.')[0]
    print(repo_name)
    clone_repo_with_name(repo_path, location, repo_name)

def clone_repo_with_name(repo_path, location, name):
    try:
        print("Cloning " + name)
        repo = Repo.clone_from(repo_path, location)
        print("Cloned Successfully")
        return repo
    except:
        print("Error While Cloning " + repo_path)