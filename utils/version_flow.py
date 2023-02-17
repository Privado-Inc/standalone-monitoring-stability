import os
from utils.clone_repo import clone_repo_with_name
from utils.build_binary import build_binary_and_move


def check_update():
    cwd = os.getcwd()
    temp_dir = f'{cwd}/temp'

    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)

    clone_repo_with_name("https://github.com/Privado-Inc/privado-core", f'{temp_dir}/joern/first/privado-core', "privado-core")

    clone_repo_with_name("https://github.com/Privado-Inc/privado-core", f'{temp_dir}/joern/second/privado-core', "privado-core")

    clone_repo_with_name("https://github.com/Privado-Inc/privado", f'{temp_dir}/privado', "privado")

    os.system(f'chmod 777 {temp_dir}/joern/second/updateDependencies.sh')

    check_command = f'cd {temp_dir}/joern/second/privado-core/ && ./updateDependencies.sh --non-interactive'
    output = os.popen(check_command).read()
    update_require = is_update_require(output)

    if update_require is None:
        return ["Error", "Error in fetching the Version"]
    if not update_require:
        return ["Updated", None]

    versions = get_updated_version(output)
    return versions


def is_update_require(output):
    print(output)
    for line in output.split('\n'):
        if 'joern' in line:
            if 'unchanged' in line:
                return False
            else:
                return True
    return None


def get_updated_version(output):
    for line in output.split('\n'):
        if 'joern' in line:
            versions = line.split(':')[-1]
            older_version = versions.split('->')[0].strip()
            newer_version = versions.split('->')[1].strip()
            return [older_version, newer_version]
    return None


def build_binary_for_joern(versions):
    # Build binary for current version
    try:
        build_binary_and_move(None, versions[0], False, f'{os.getcwd()}/joern/first/privado-core')
    except Exception as e:
        print(f'Binary not generating for joern version {versions[0]}', e)
        return False

    try:
        build_binary_and_move(None, versions[1], False, f'{os.getcwd()}/joern/second/privado-core')
    except Exception as e:
        print(f'Binary not generating for joern version {versions[1]}', e)
        return False

    return True

