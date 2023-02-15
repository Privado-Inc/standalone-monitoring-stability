import csv
import os
import openpyxl
from openpyxl.styles import PatternFill, Font



def create_new_excel_for_file(location, first_file, second_file):
    wb = openpyxl.Workbook()
    # Delete the default sheet
    wb.remove(wb.active)
    # Create new Sheet
    wb.create_sheet('scan-status')
    wb.create_sheet('source-&-sink-report')
    wb.create_sheet('flow-report')
    wb.save(location)


def create_new_excel(location, base_branch_name, head_branch_name):
    wb = openpyxl.Workbook()
    # Delete the default sheet
    wb.remove(wb.active)
    # Create new Sheet
    wb.create_sheet('summary')
    wb.create_sheet('scan-status')
    wb.create_sheet(f'{head_branch_name}-{base_branch_name}-source-&-sink-report')
    wb.create_sheet(f'{head_branch_name}-{base_branch_name}-flow-report')
    wb.create_sheet(f'{head_branch_name}-{base_branch_name}-performance-report')
    wb.save(location)


def write_source_sink_data(workbook_location, worksheet_name, report):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    worksheet = workbook[worksheet_name]

    for row in report:
        worksheet.append(row)

    workbook.save(workbook_location)


def write_path_data(workbook_location, worksheet_name, report):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    worksheet = workbook[worksheet_name]

    for row in report:
        worksheet.append(row)

    workbook.save(workbook_location)


def write_performance_data(workbook_location, worksheet_name, report):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    worksheet = workbook[worksheet_name]

    for row in report:
        worksheet.append(row)

    workbook.save(workbook_location)


def write_scan_status_report_for_file(workbook_location, base_branch_name, head_branch_name, report):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    worksheet = workbook['scan-status']

    for line in report:
        worksheet.append(line)

    workbook.save(workbook_location)


def write_scan_status_report(workbook_location, base_branch_name, head_branch_name, report):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    worksheet = workbook['scan-status']

    worksheet.append(
        ["Repo", "Branch", "language" ,"scan status", "scan error", "comparison status", "comparison error", "unique flow count",
         "scan time (ms)", "CPG size"])


    for repo in report.keys():
        repo_info = report[repo]
        worksheet.append([repo, base_branch_name, report[repo]['language'] ,repo_info[base_branch_name]['scan_status'],
                          repo_info[base_branch_name]['scan_error_message'],
                          repo_info[base_branch_name]['comparison_status'],
                          repo_info[base_branch_name]['comparison_error_message'],
                          repo_info[base_branch_name]['unique_flows'],
                          repo_info[base_branch_name]['code_scan_time'],
                          repo_info[base_branch_name]['binary_file_size']])

        worksheet.append([repo, head_branch_name, report[repo]['language'],repo_info[head_branch_name]['scan_status'],
                          repo_info[head_branch_name]['scan_error_message'],
                          repo_info[head_branch_name]['comparison_status'],
                          repo_info[head_branch_name]['comparison_error_message'],
                          repo_info[head_branch_name]['unique_flows'],
                          repo_info[head_branch_name]['code_scan_time'],
                          repo_info[head_branch_name]['binary_file_size']])

    workbook.save(workbook_location)


def write_summary_data(workbook_location, base_branch_name, head_branch_name, report, data_elements, missing_sinks):
    print("Data elements: " , data_elements)
    workbook = openpyxl.load_workbook(filename=workbook_location)
    worksheet = workbook['summary']

    worksheet.append(["Repo", "language" ,"scan status", f"{base_branch_name} Scan status <Base - head> (ms)", f"{head_branch_name} scan time (ms)",
                      "scan time diff (ms)", "Reachable by flow diff (ms)", f"{base_branch_name} unique flows",
                      f"{head_branch_name} unique flows", "unique flows diff",  
                      f"{base_branch_name} No of data elements",
                      f"{head_branch_name} No of data elements", "Data element diff",
                      f"Missing sinks in {head_branch_name}",
                      "No of 100% missing source to sink combinations"])

    scan_time_positive = 0
    scan_time_positive_average = 0
    scan_time_negative_average = 0

    reachable_by_flow_time_positive = 0
    reachable_by_flow_time_positive_average = 0
    reachable_by_flow_time_negative_average = 0

    matching_flows = 0
    more_flows = 0
    less_flows = 0

    more_sources = 0
    less_sources = 0
    matching_sources = 0

    missing_sink_repo_count = len(list(filter(lambda x: x > 0, missing_sinks.values())))
    missing_sink_average = sum(missing_sinks.values()) / missing_sink_repo_count if missing_sink_repo_count > 0 else 0


    for repo in report.keys():
        scan_status = 'done' if report[repo][head_branch_name]['comparison_error_message'] == '--' and report[repo][base_branch_name]['comparison_error_message'] == '--' else 'failed'
        head_scan_time = report[repo][head_branch_name]['code_scan_time'].split()[0]
        base_scan_time = report[repo][base_branch_name]['code_scan_time'].split()[0]
        language = report[repo]['language']
        scan_time_diff = '--' if base_scan_time == '--' or head_scan_time == '--' else int(head_scan_time) - int(base_scan_time)

        print("Scan time diff: " , scan_time_diff)
        if (scan_time_diff != '--'):
            if (scan_time_diff > 0): # Head branch took more time
                scan_time_positive += 1
                scan_time_positive_average += scan_time_diff
            else:
                scan_time_negative_average += (scan_time_diff*-1)



        unique_flow_diff = '--' if report[repo][base_branch_name]['unique_flows'] == '--' or report[repo][head_branch_name]['unique_flows'] == '--' else int(report[repo][head_branch_name]['unique_flows']) - int(report[repo][base_branch_name]['unique_flows'])

        if (unique_flow_diff != '--'):
            if (unique_flow_diff > 0):
                more_flows += 1
            elif unique_flow_diff < 0:
                less_flows += 1
            else:
                matching_flows += 1


        unique_source_diff = '--' if data_elements[repo][base_branch_name] == '--' or data_elements[repo][head_branch_name] == '--' else int(data_elements[repo][head_branch_name]) - int(data_elements[repo][base_branch_name])
        
        if (unique_source_diff != '--'):
            if (unique_source_diff > 0):
                more_sources += 1
            elif unique_source_diff < 0:
                less_sources += 1
            else:
                matching_sources += 1

        
        reachable_flow_time_diff = '--' if report[repo][base_branch_name]['reachable_flow_time'] == '--' or report[repo][head_branch_name]['reachable_flow_time'] == '--' else int(report[repo][head_branch_name]['reachable_flow_time']) - int(report[repo][base_branch_name]['reachable_flow_time'])


        print(reachable_flow_time_diff)
        if (reachable_flow_time_diff != '--'):
            if (reachable_flow_time_diff > 0): # Head branch took more time
                reachable_by_flow_time_positive += 1
                reachable_by_flow_time_positive_average += reachable_flow_time_diff
            else:
                reachable_by_flow_time_negative_average += (reachable_flow_time_diff*-1)


        worksheet.append([repo ,language , scan_status, base_scan_time, head_scan_time, scan_time_diff,
                          reachable_flow_time_diff,
                          report[repo][base_branch_name]['unique_flows'],
                          report[repo][head_branch_name]['unique_flows'], unique_flow_diff,
                          data_elements[repo][base_branch_name],
                          data_elements[repo][head_branch_name], unique_source_diff,
                          report[repo]['missing_sink'],
                         "---"])
        print(report[repo]['missing_sink'])

    print(scan_time_positive, len(report.keys()) - scan_time_positive, scan_time_negative_average)
    # cannot divide by zero
    scan_time_positive_average = scan_time_positive_average / scan_time_positive if scan_time_positive > 0 else 0 # Average of more time repos
    scan_time_negative_average = (scan_time_negative_average / (len(report.keys()) - scan_time_positive)) if (len(report.keys()) - scan_time_positive) > 0 else 0 # Average of less time repos
    
    reachable_by_flow_time_positive_average = reachable_by_flow_time_positive_average / reachable_by_flow_time_positive if reachable_by_flow_time_positive > 0 else 0 # Average of more time repos
    reachable_by_flow_time_negative_average = reachable_by_flow_time_negative_average / (len(report.keys()) - reachable_by_flow_time_positive) if (len(report.keys()) - reachable_by_flow_time_positive) > 0 else 0 # Average of less time repos

    write_slack_summary(f'''
        A. Scantime difference.
        {scan_time_positive} repos took an average {scan_time_positive_average} ms more.
        {len(report.keys()) - scan_time_positive} repos took an average {scan_time_negative_average} ms  less.

        B. Reachable by flow time difference.
        {reachable_by_flow_time_positive} repos took an average {reachable_by_flow_time_positive_average} ms more.
        {len(report.keys()) - reachable_by_flow_time_positive} repos took an average {reachable_by_flow_time_negative_average} ms less.

        C. Reachable by flow count difference.
        {matching_flows} repositories have exactly matching flows.
        {less_flows} repositories have missing flows.
        {more_flows} repositories have additional flows.

        D. Unique data elements difference.
        {matching_sources} repositories have exactly matching elements.
        {less_sources} repositories have missing data elements.
        {more_sources} repositories have additional elements.

        E. Missing sinks.
        {missing_sink_repo_count} repositories have an average {missing_sink_average} missing sinks.

        F.       
    ''')
    
    print(scan_time_positive)
    print(scan_time_negative_average, scan_time_positive_average)

    highlight_summary_cell(worksheet)
    workbook.save(workbook_location)


def highlight_summary_cell(worksheet):

    for col in ['F', 'G', 'J', 'M', 'N']:
        for row in range(2, len(worksheet[col]) + 1):
            if int(worksheet[f'{col}{row}'].value) < 0:
                worksheet[f'{col}{row}'].fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type = "solid")
                worksheet[f'{col}{row}'].font = Font(color='FFFFFF')
            else:
                worksheet[f'{col}{row}'].fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
                worksheet[f'{col}{row}'].font = Font(color='FFFFFF')


    
def write_slack_summary(statement):
    with open(f"{os.getcwd()}/slack_summary.txt", "a") as slack_summary:
        slack_summary.writelines(statement)