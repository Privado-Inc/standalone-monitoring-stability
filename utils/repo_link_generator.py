def generate_repo_link(filename):
    repo_content = open(filename)

    for repo in repo_content.read().split('\n'):
        yield repo