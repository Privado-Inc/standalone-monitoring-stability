import utils.repo_link_generator
from utils.scan import scan_repo_report
from utils.compare import main as compare_and_generate_report, compare_files
from utils.post_to_slack import post_report_to_slack
from utils.build_binary import build
from utils.delete import delete_action, clean_after_scan
from utils.clone_repo import clone_repo_with_location
from utils.write_to_file import create_new_excel, write_scan_status_report, write_summary_data
from utils.scan import get_detected_language
import os
import argparse
import traceback

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("-r", "--repos", default=f"{os.getcwd()}/repos.txt")
parser.add_argument('--upload', action='store_true')
parser.add_argument('--no-upload', dest='feature', action='store_false')
parser.add_argument("-b", "--base", default=None)
parser.add_argument('-h', "--head", default=None)
parser.add_argument('-nc', action='store_true')
parser.add_argument('-bs', "--boost", default=False)
parser.add_argument('-m', action='store_true')
parser.add_argument('-d', '--use-docker', action='store_true')
parser.set_defaults(feature=True)

args: argparse.Namespace = parser.parse_args()


def workflow():
    args.base = args.base.replace('/', '-')
    args.head = args.head.replace('/', '-')
    print(args.base, args.head)
    # check if branch name present in args
    if args.base is None or args.head is None:
        print("Please provide flags '-h' and '-b' followed by branch name")
        return

    cwd = os.getcwd()

    # Delete previously scanned Excel report if exist
    excel_report_location = f'{cwd}/output.xlsx'
    if os.path.isfile(excel_report_location):
        os.remove(excel_report_location)

    # When Privado.json files provided
    if args.m:
        compare_files(args.base, args.head)
        return

    create_new_excel(excel_report_location, args.base, args.head)
    valid_repositories = []

    # Cleanup action
    delete_action(args.nc, args.boost)

    if not args.use_docker:
        # build the Privado binary for both branches
        build(args.base, args.head, args.boost)

    try:
        for repo_link in utils.repo_link_generator.generate_repo_link(args.repos):
            try:
                repo_name = repo_link.split('/')[-1].split('.')[0]
                is_git_url: bool = utils.repo_link_generator.check_git_url(repo_link)
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                continue

            location = cwd + "/temp/repos/" + repo_name
            os.system("mkdir -p " + location)
            clone_repo_with_location(repo_link, location, is_git_url)
            valid_repositories.append(repo_name)

        scan_status = scan_repo_report(args.base, args.head, valid_repositories, use_docker=args.use_docker)

        # Used to add header for only one time in report
        header_flag = True

        for repo_name in valid_repositories:
            try:
                base_file = f'{cwd}/temp/result/{args.base}/{repo_name}.json'
                head_file = f'{cwd}/temp/result/{args.head}/{repo_name}.json'
                detected_language = get_detected_language(repo_name, args.base)
                compare_and_generate_report(base_file, head_file, args.base, args.head, header_flag, scan_status, detected_language)
                scan_status[repo_name][args.base]['comparison_status'] = 'done'
                scan_status[repo_name][args.base]['comparison_error_message'] = '--'
                scan_status[repo_name][args.head]['comparison_status'] = 'done'
                scan_status[repo_name][args.head]['comparison_error_message'] = '--'
            except Exception as e:
                print(f'{repo_name}: comparison report not generating: {e}')
                scan_status[repo_name][args.base]['comparison_status'] = 'failed'
                scan_status[repo_name][args.base]['comparison_error_message'] = str(e)
                scan_status[repo_name][args.head]['comparison_status'] = 'failed'
                scan_status[repo_name][args.head]['comparison_error_message'] = str(e)
            header_flag = False

        write_scan_status_report(f'{cwd}/output.xlsx', args.base, args.head, scan_status)
        write_summary_data(f'{cwd}/output.xlsx', args.base, args.head, scan_status)

        if args.upload:
            post_report_to_slack()
    except Exception as e:
        traceback.print_exc()
        print(f"An exception occurred {str(e)}")

    finally:
        clean_after_scan(args.boost)


workflow()
