import utils.repo_link_generator
from utils.scan import scan_repo_report
from utils.compare import main as compare_and_generate_report, compare_files, process_sources, process_sinks, process_path_analysis
from utils.post_to_slack import post_report_to_slack
from utils.build_binary import build
from utils.delete import delete_action, clean_after_scan
from utils.clone_repo import clone_repo_with_location
from utils.write_to_file import create_new_excel, write_scan_status_report, write_summary_data
from utils.scan import get_detected_language
from utils.version_flow import check_update, build_binary_for_joern
from utils.write_to_file import write_slack_summary
import os
import argparse
import traceback
import json

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
parser.add_argument('-guf', '--generate-unique-flow', action='store_true')
parser.add_argument('-ju', '--joern-update', action='store_true')
parser.add_argument('-rbb', '--rules-branch-base', default=None)
parser.add_argument('-rbh', '--rules-branch-head', default=None)
parser.set_defaults(feature=True)

args: argparse.Namespace = parser.parse_args()


def workflow():
    print(args.rules_branch)
    # Cleanup action
    delete_action(args.nc, args.boost)

    base_worksheet_name = args.base.replace('/', '-')
    head_worksheet_name = args.head.replace('/', '-')

    if os.path.isfile(f'{os.getcwd()}/slack_summary.txt'):
        os.system(f'rm {os.getcwd()}/slack_summary.txt')

    if args.joern_update:
        versions = check_update()
        if versions == 'updated':
            print("No Update Available")
            write_slack_summary(f"Current version: {versions[0]} \n Updated Version: {versions[1]} \n No Update Available for Comparison")
            post_report_to_slack(False)
            return
        else:
            if not build_binary_for_joern(versions):
                post_report_to_slack(False)
                return
            args.base = versions[0]
            args.head = versions[1]

    # check if branch name present in args
    if args.base is None or args.head is None:
        print("Please provide flags '-h' and '-b' followed by value")
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

    create_new_excel(excel_report_location, base_worksheet_name, head_worksheet_name)
    valid_repositories = []

    if not args.use_docker and not args.joern_update:
        # build the Privado binary for both branches
        build(args.base, args.head, args.rules_branch,args.boost)

    # Remove slack summary if already present
    if (os.path.isfile(f"{cwd}/slack_summary.txt")):
        os.remove(f"{cwd}/slack_summary.txt")

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

        scan_status = scan_repo_report(args.base, args.head, valid_repositories, args.use_docker, args.generate_unique_flow,rules_branch_base, rules_branch_head)
        source_count = dict()
        flow_data = dict()

        # Used to add header for only one time in report
        header_flag = True

        for repo_name in valid_repositories:
            try:
                base_file = f'{cwd}/temp/result/{args.base}/{repo_name}.json'
                head_file = f'{cwd}/temp/result/{args.head}/{repo_name}.json'
                detected_language = get_detected_language(repo_name, args.base)
                base_intermediate_file = f'{cwd}/temp/result/{args.base}/{repo_name}-intermediate.json'
                head_intermediate_file = f'{cwd}/temp/result/{args.head}/{repo_name}-intermediate.json'
                compare_and_generate_report(base_file, head_file, args.base, args.head, base_intermediate_file, head_intermediate_file, header_flag, scan_status, detected_language)
                
                scan_status[repo_name][args.base]['comparison_status'] = 'done'
                scan_status[repo_name][args.base]['comparison_error_message'] = '--'
                scan_status[repo_name][args.head]['comparison_status'] = 'done'
                scan_status[repo_name][args.head]['comparison_error_message'] = '--'

                try:
                    base_file = open(base_file)
                    head_file = open(head_file)

                    base_data = json.load(base_file)
                    head_data = json.load(head_file)                
                except Exception as e:
                    print("File not loaded")
                    print(e)



                try:
                    source_data = process_sources(base_data['sources'], head_data['sources'], repo_name, detected_language) # Get the source data from the process_sources function
                    storage_data = process_sinks(base_data['dataFlow'], head_data['dataFlow'], repo_name,scan_status ,detected_language, key='storages')
                    third_parties_data = process_sinks(base_data['dataFlow'], head_data['dataFlow'], repo_name,scan_status ,detected_language, key='third_parties')
                    leakages_data = process_sinks(base_data['dataFlow'], head_data['dataFlow'], repo_name,scan_status ,detected_language, key='leakages')
                    flow_report = process_path_analysis(f'{head_worksheet_name}-{base_worksheet_name}-flow-report', base_data, head_data, repo_name, args.base, args.head, detected_language, False)
                    missing_flow_head = flow_report[0][-2]
                    additional_flow_head = flow_report[0][-3]
                    matching_flows = 0

                    hundred_percent_missing_repos = 0
                    for flow in flow_report:
                        if (flow[-3] == '-100%' or flow[-3] == '-100'):
                            hundred_percent_missing_repos += 1

                except Exception as e: 
                    print(e)

                flow_data[repo_name] = dict({'missing': missing_flow_head, 'additional': additional_flow_head, 'hundred_missing': hundred_percent_missing_repos, 'matching_flows': True if flow_report[0][-3] == '0' else False})
                source_count[repo_name] = dict({args.base: source_data[5], args.head: source_data[4]})

                base_file.close()
                head_file.close()
            except Exception as e:
                print(f'{repo_name}: comparison report not generating: {e}')
                scan_status[repo_name][args.base]['comparison_status'] = 'failed'
                scan_status[repo_name][args.base]['comparison_error_message'] = str(e)
                scan_status[repo_name][args.head]['comparison_status'] = 'failed'
                scan_status[repo_name][args.head]['comparison_error_message'] = str(e)
            header_flag = False

        write_scan_status_report(f'{cwd}/output.xlsx', args.base, args.head, scan_status)
        write_summary_data(f'{cwd}/output.xlsx', args.base, args.head, scan_status, source_count, flow_data)

        if args.upload or args.joern_update:
            post_report_to_slack(True)
    except Exception as e:
        traceback.print_exc()
        print(f"An exception occurred {str(e)}")

    finally:
        clean_after_scan(args.boost)


workflow()
