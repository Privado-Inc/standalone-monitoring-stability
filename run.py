import utils.repo_link_generator
from utils.scan import scan_repo_report
from utils.compare import main as compare_and_generate_report
from utils.post_to_slack import post_report_to_slack
from utils.build_binary import build
from utils.delete import delete_action, clean_after_scan
from utils.clone_repo import clone_repo_with_location
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--repos", default=f"{os.getcwd()}/repos.txt")
parser.add_argument('--upload', action='store_true')
parser.add_argument('--no-upload', dest='feature', action='store_false')
parser.add_argument("-f", "--first", default = None)
parser.add_argument('-s', "--second", default=None)
parser.add_argument('-c', action='store_true')
parser.set_defaults(feature=True)

args = parser.parse_args()
def workflow():

    # check if branch name present in args
    if args.first == None or args.second == None:
        print("Please provide flags '-f' and '-s' followed by branch name")
        return

    valid_repositories = []
    cwd = os.getcwd()
    
    delete_action(args.c)

    # build the privado binary for both branches 
    build(args.first, args.second)

    # Delete previous scan report if exist
    path = f'{cwd}/comparison_report.csv'
    if os.path.isfile(path):
        os.remove(path)

    try: 
        for repo_link in utils.repo_link_generator.generate_repo_link(args.repos):
            try:
                repo_name = repo_link.split('/')[-1].split('.')[0]
            except:
                print("Not a valid git repository")
                continue
            location = cwd + "/temp/repos/" + repo_name
            os.system("mkdir -p " + location)
            valid_repositories.append(repo_name)
            clone_repo_with_location(repo_link, location) 

        scan_repo_report(args.first, args.second)
        
        for repo_name in valid_repositories:
            stable_file = f'{cwd}/temp/result/{args.first}/{repo_name}.json'
            dev_file = f'{cwd}/temp/result/{args.second}/{repo_name}.json'
            cpu_usage = f'{cwd}/temp/cpu_mem/{repo_name}_cpu_mem.txt'
            stable_time = f'{cwd}/temp/result/{args.first}/{repo_name}_time.txt'
            dev_time = f'{cwd}/temp/result/{args.second}/{repo_name}_time.txt'
            compare_and_generate_report(stable_file, dev_file, cpu_usage, stable_time, dev_time)

        if (args.upload): post_report_to_slack()
    except Exception as e:
        print("An exception occurred " + str(e))
    finally:
        clean_after_scan()

workflow()
