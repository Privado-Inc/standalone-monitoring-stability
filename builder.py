import config
import os
from datetime import datetime

pwd = os.getcwd()

SLACK_SUMMARY_PATH = f'{pwd}/{config.SLACK_SUMMARY_FILE_NAME}'
OUTPUT_PATH = f'{pwd}/{config.OUTPUT_FILE_NAME}'


def get_current_time():
    current_time = datetime.utcnow()
    return f'{str(current_time.strftime("%Y-%m-%d %I:%M:%S %p"))} UTC'


def get_result_path(branch, repo):
    return f'{pwd}/temp/result/{branch}/{repo}.json'


def get_intermediate_path(branch, repo):
    return f'{pwd}/temp/result/{branch}/{repo}-intermediate.json'


def get_repo_path(repo):
    return f'{pwd}/temp/repos/{repo}'


def get_joern_update_file_path(path):
    return f'{pwd}/temp/joern/{path}/privado-core/updateDependencies.sh'


def get_joern_privado_path(path):
    return f'{pwd}/temp/joern/{path}/privado-core'


def get_privado_path(version):
    return f'{pwd}/temp/privado/Privado-Inc-{version}#Privado-Inc-dev'
