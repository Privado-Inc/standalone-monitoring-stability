import utils.clone_repo as clone_utils
import utils.repo_link_generator
from utils.scan import scan_repo_report
from utils.compare import main as compare_and_generate_report
from utils.delete import delete_temp
from utils.post_to_slack import post_report_to_slack
import sys
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", default=f"{os.getcwd()}/repos.txt")
parser.add_argument('--upload', action='store_true')
parser.add_argument('--no-upload', dest='feature', action='store_false')
parser.set_defaults(feature=True)

args = parser.parse_args()

def workflow():
    valid_repositories = []
    cwd = os.getcwd()
    clone_utils.install_privado()

    # Delete previous scan report if exist
    path = f'{cwd}/comparison_report.csv'
    if os.path.isfile(path):
        os.remove(path)

    try: 
        for repo_link in utils.repo_link_generator.generate_repo_link(args.file):
            try:
                repo_name = repo_link.split('/')[-1].split('.')[0]
            except:
                print("Not a valid git repository")
                continue
            valid_repositories.append(repo_name)
            clone_utils.clone_repo(repo_link)

        scan_repo_report()
        
        for repo_name in valid_repositories:
            stable_file = f'{cwd}/temp/result/stable/{repo_name}.json'
            dev_file = f'{cwd}/temp/result/dev/{repo_name}.json'
            cpu_usage = f'{cwd}/temp/cpu_mem/{repo_name}_cpu_mem.txt'
            stable_time = f'{cwd}/temp/result/stable/{repo_name}_time.txt'
            dev_time = f'{cwd}/temp/result/dev/{repo_name}_time.txt'
            compare_and_generate_report(stable_file, dev_file, cpu_usage, stable_time, dev_time)

        if (args.upload): post_report_to_slack()
    except:
        print("An exception occurred")
    finally:
        delete_temp()

workflow()
