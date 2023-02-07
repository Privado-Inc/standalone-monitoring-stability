import utils.repo_link_generator
from utils.scan import scan_repo_report
from utils.compare import main as compare_and_generate_report, compare_files
from utils.post_to_slack import post_report_to_slack
from utils.build_binary import build
from utils.delete import delete_action, clean_after_scan
from utils.clone_repo import clone_repo_with_location
import os
import argparse
import traceback

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--repos", default=f"{os.getcwd()}/repos.txt")
parser.add_argument('--upload', action='store_true')
parser.add_argument('--no-upload', dest='feature', action='store_false')
parser.add_argument("-f", "--first", default=None)
parser.add_argument('-s', "--second", default=None)
parser.add_argument('-c', action='store_true')
parser.add_argument('-b', "--boost", default=False)
parser.add_argument('-m', action='store_true')
parser.add_argument('-d', '--use-docker', action='store_true')
parser.set_defaults(feature=True)

args: argparse.Namespace = parser.parse_args()


def workflow():
    # check if branch name present in args
    if args.first is None or args.second is None:
        print("Please provide flags '-f' and '-s' followed by branch name")
        return

    cwd = os.getcwd()

    # Delete previous scan Excel report if exist
    excel_report_location = f'{cwd}/output.xlsx'
    if os.path.isfile(excel_report_location):
        os.remove(excel_report_location)

    # When Privado.json files provided
    if args.m:
        compare_files(args.first, args.second)
        return

    valid_repositories = []

    delete_action(args.c, args.boost)

    if (not args.use_docker):
        # build the Privado binary for both branches
        build(args.first, args.second, args.boost)
        

    # Delete previous scan report if exist
    path = f'{cwd}/comparison_report.csv'
    if os.path.isfile(path):
        os.remove(path)

    try:
        for repo_link in utils.repo_link_generator.generate_repo_link(args.repos):
            try:
                repo_name = repo_link.split('/')[-1].split('.')[0]
                print(repo_link)
                is_git_url: bool = utils.repo_link_generator.check_git_url(repo_link)
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                continue

            location = cwd + "/temp/repos/" + repo_name
            os.system("mkdir -p " + location)
            clone_repo_with_location(repo_link, location, is_git_url)
            valid_repositories.append(repo_name)

        scan_status = scan_repo_report(args.first, args.second, use_docker=args.use_docker)



        # Used to add header for only one time in report
        header_flag = True

        for repo_name in valid_repositories:
            if (scan_status[f'{repo_name},{args.first}'] == 'failed' or scan_status[f'{repo_name},{args.second}'] == 'failed'): continue
            stable_file = f'{cwd}/temp/result/{args.first}/{repo_name}.json'
            dev_file = f'{cwd}/temp/result/{args.second}/{repo_name}.json'
            stable_time = f'{cwd}/temp/result/{args.first}/{repo_name}_time.txt'
            dev_time = f'{cwd}/temp/result/{args.second}/{repo_name}_time.txt'
            compare_and_generate_report(stable_file, dev_file, stable_time, dev_time, args.first,
                                        args.second, header_flag)
            header_flag = False

        if args.upload:
            post_report_to_slack()
    except Exception as e:
        traceback.print_exc()
        print(f"An exception occurred {str(e)}")

    finally:
        clean_after_scan(args.boost)


workflow()
