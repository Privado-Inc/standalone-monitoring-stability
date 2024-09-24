import utils.repo_link_generator
from utils.helpers import print_timestamp
from utils.scan import scan_repo_report
from utils.compare import main as compare_and_generate_report, compare_files, process_sources, process_sinks, process_path_analysis, process_collection, top_level_collection_processor, sub_process_occurrences
from utils.post_to_slack import post_report_to_slack
from utils.build_binary import build
from utils.delete import delete_action, clean_after_scan
from utils.clone_repo import clone_repo_with_location, clone_joern_and_checkout, checkIfBranchExist
from utils.write_to_file import create_new_excel, write_scan_status_report, write_summary_data, write_to_action_result
from utils.scan import get_detected_language
from utils.version_flow import check_update, build_binary_for_joern
from utils.write_to_file import write_slack_summary
from utils.build_binary import publish_joern_and_get_version
import builder
import config
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
parser.add_argument('-urc', '--use-rule-compare', action='store_true')
parser.add_argument('-dm', '--debug-mode', action='store_true')
parser.add_argument('-bcr', '--base-core-repo', default=None)
parser.add_argument('-hcr', '--head-core-repo', default=None)
parser.add_argument('-brr', '--base-rule-repo', default=None)
parser.add_argument('-hrr', '--head-rule-repo', default=None)
parser.add_argument("--custom-joern", default=False)
parser.add_argument("--custom-joern-base-branch", default=None)
parser.add_argument("--custom-joern-head-branch", default=None)
parser.add_argument('--token', default=None)
parser.set_defaults(feature=True)

args: argparse.Namespace = parser.parse_args()


def workflow():

    print_timestamp("Comparison script started")

    # Cleanup action
    delete_action(args.nc, args.boost)

    # Remove slack summary if already present
    if os.path.isfile(builder.SLACK_SUMMARY_PATH):
        os.system(f'rm {builder.SLACK_SUMMARY_PATH}')

    if args.joern_update:
        versions = check_update(args.token)
        if versions[0] == 'updated':
            print_timestamp("No Update Available for comparison")
            write_slack_summary(
                f"No Update Available for Comparison")
            post_report_to_slack(False)
        args.base = versions[0]
        args.head = versions[1]

    if args.custom_joern:
        checkIfBranchExist(args)

    print(" -----ffgggggg- " + args.head)

    if not args.m:
        config.init(args)
    else:
        config.init_file(args)

    if args.joern_update:
        if not build_binary_for_joern(versions):
            post_report_to_slack(False)
            return

    if args.use_rule_compare:
        if args.rules_branch_base is None or args.rules_branch_head is None:
            print("Please provide flags \"-rbb=\" and \"-rbh\" while using \"-urc\" flag")
            return

    if args.custom_joern:
        print("Custom joern build")
        if (args.custom_joern_base_branch is not None and args.custom_joern_head_branch is not None):
            clone_joern_and_checkout(args.custom_joern_base_branch, args.boost)
            publish_joern_and_get_version(args.custom_joern_base_branch)
            clone_joern_and_checkout(args.custom_joern_head_branch, args.boost)
            publish_joern_and_get_version(args.custom_joern_head_branch)
        else:
            print("Error: Did not specify branch for custom joern build.")


    # Delete previously scanned Excel report if exist
    excel_report_location = config.OUTPUT_FILE_NAME
    if os.path.isfile(excel_report_location):
        os.remove(excel_report_location)

    # When Privado.json files provided
    if args.m:
        compare_files(args.base, args.head)
        return

    base_worksheet_name = config.BASE_SHEET_BRANCH_NAME.replace('/', '-')
    head_worksheet_name = config.HEAD_SHEET_BRANCH_NAME.replace('/', '-')

    create_new_excel(excel_report_location, base_worksheet_name, head_worksheet_name)
    valid_repositories = []

    if not args.use_docker and not args.joern_update:
        # build the Privado binary for both branches
        build(args, args.boost, args.custom_joern, args.custom_joern_base_branch, args.custom_joern_head_branch)

    try:
        for repo_link in utils.repo_link_generator.generate_repo_link(args.repos):
            try:
                repo_name = repo_link.split('/')[-1].split('.')[0]
                is_git_url: bool = utils.repo_link_generator.check_git_url(repo_link)
            except Exception as e:
                print(str(e))
                traceback.print_exc()
                continue

            location = builder.get_repo_path(repo_name)
            os.system("mkdir -p " + location)
            clone_repo_with_location(repo_link, location, is_git_url)
            valid_repositories.append(repo_name)

        source_count = dict()
        flow_data = dict()
        collection_count = dict()

        # Used to add header for only one time in report
        header_flag = True
        scan_status = scan_repo_report(valid_repositories, args)

        for repo_name in valid_repositories:
            try:
                base_file = builder.get_result_path(config.BASE_CORE_BRANCH_KEY, repo_name)
                head_file = builder.get_result_path(config.HEAD_CORE_BRANCH_KEY, repo_name)
                detected_language = get_detected_language(repo_name, config.BASE_CORE_BRANCH_KEY)
                base_intermediate_file = builder.get_intermediate_path(config.BASE_CORE_BRANCH_KEY, repo_name)
                head_intermediate_file = builder.get_intermediate_path(config.HEAD_CORE_BRANCH_KEY, repo_name)
                compare_and_generate_report(base_file, head_file, base_intermediate_file, head_intermediate_file, header_flag, scan_status, detected_language)

                scan_status[repo_name][config.BASE_CORE_BRANCH_KEY]['comparison_status'] = 'done'
                scan_status[repo_name][config.BASE_CORE_BRANCH_KEY]['comparison_error_message'] = '--'
                scan_status[repo_name][config.HEAD_CORE_BRANCH_KEY]['comparison_status'] = 'done'
                scan_status[repo_name][config.HEAD_CORE_BRANCH_KEY]['comparison_error_message'] = '--'

                base_data = dict()
                head_data = dict()
                try:
                    base_file = open(base_file)
                    head_file = open(head_file)

                    base_data = json.load(base_file)
                    head_data = json.load(head_file)
                except Exception as e:
                    print("File not loaded")
                    print(e)


                missing_flow_head = 0
                additional_flow_head = 0
                source_data = list()
                collections_data = list()
                hundred_percent_missing_repos = 0
                flow_report = list()
                try:
                    # Get the source data from the process_sources function
                    source_data = process_sources(base_data['sources'], head_data['sources'], repo_name, detected_language)
                    flow_report = process_path_analysis(f'{head_worksheet_name}-{base_worksheet_name}-flow-report', base_data, head_data, repo_name, detected_language, False, False)
                    collections_data = sub_process_occurrences(base_data['collections'], head_data['collections'], repo_name, detected_language)[-1]


                    missing_flow_head = flow_report[0][-2]
                    additional_flow_head = flow_report[0][-3]

                    for flow in flow_report:
                        if flow[-3] == '-100%' or flow[-3] == '-100':
                            hundred_percent_missing_repos += 1

                    flow_data[repo_name] = dict({'missing': missing_flow_head, 'additional': additional_flow_head,
                                                 'hundred_missing': hundred_percent_missing_repos,
                                                 'matching_flows': True if flow_report[0][-3] == 0 else False})
                    source_count[repo_name] = dict(
                        {config.BASE_CORE_BRANCH_KEY: source_data[5], config.HEAD_CORE_BRANCH_KEY: source_data[4]})
                    collection_count[repo_name] = dict({config.BASE_CORE_BRANCH_KEY: collections_data[1],
                                                        config.HEAD_CORE_BRANCH_KEY: collections_data[0]})

                    base_file.close()
                    head_file.close()
                except KeyError as key:
                    write_to_action_result(f"{key} key not found in either the source or head branch")
                except Exception as ex:
                    write_to_action_result(ex)


            except Exception as e:
                traceback.print_exc()
                print_timestamp(f'{repo_name}: comparison report not generating: {e}')
                scan_status[repo_name][config.BASE_CORE_BRANCH_KEY]['comparison_status'] = 'failed'
                scan_status[repo_name][config.BASE_CORE_BRANCH_KEY]['comparison_error_message'] = str(e)
                scan_status[repo_name][config.HEAD_CORE_BRANCH_KEY]['comparison_status'] = 'failed'
                scan_status[repo_name][config.HEAD_CORE_BRANCH_KEY]['comparison_error_message'] = str(e)
            header_flag = False

        try:
            write_scan_status_report(builder.OUTPUT_PATH, scan_status)
        except Exception as ex:
            print(ex)
        write_summary_data(builder.OUTPUT_PATH, scan_status, source_count, collection_count , flow_data)

        if args.upload or args.joern_update:
            post_report_to_slack(True)
    except Exception as e:
        traceback.print_exc()
        print_timestamp("An exception occurred {str(e)}")

    finally:
        print_timestamp(f'Comparison script Ended')
        clean_after_scan(args.boost)


workflow()
