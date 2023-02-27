import os
from urllib.parse import urlparse


def generate_repo_link(filename):
    repo_content = open(filename)

    for repo in repo_content.read().split('\n'):
        yield repo


def check_git_url(path) -> bool:
    parsed_url = urlparse(path)
    # Check if the URL has a scheme (http, https, git, etc.)
    if parsed_url.scheme:
        return True
    elif os.path.isdir(path):
        return False
    else:
        raise Exception("Invalid local path")
