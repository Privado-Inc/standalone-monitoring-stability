import csv
import os
import openpyxl
from openpyxl.styles import PatternFill, Font


def write_to_csv(filename, values):
    # filename is the name of the granular report
    # headers is an array containing the column names -
    # values is a 2D Array with each element signifying a particular row
    cwd = os.getcwd()
    file_path = f'{cwd}/{filename}.csv'

    with open(file_path, "a") as value:
        report = csv.writer(value)
        for row in values:
            report.writerow(row)


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
    wb.create_sheet('scan-status')
    wb.create_sheet('summary')
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


def write_scan_status_report(workbook_location, base_branch_name, head_branch_name, report):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    worksheet = workbook['scan-status']

    worksheet.append(
        ["Repo", "Branch", "scan status", "scan error", "comparison status", "comparison error", "unique flow count",
         "scan time", "CPG size"])

    for repo in report.keys():
        repo_info = report[repo]
        worksheet.append([repo, base_branch_name, repo_info[base_branch_name]['scan_status'],
                          repo_info[base_branch_name]['scan_error_message'],
                          repo_info[base_branch_name]['comparison_status'],
                          repo_info[base_branch_name]['comparison_error_message'],
                          repo_info[base_branch_name]['unique_flows'],
                          repo_info[base_branch_name]['code_scan_time'],
                          repo_info[base_branch_name]['binary_file_size']])

        worksheet.append([repo, head_branch_name, repo_info[head_branch_name]['scan_status'],
                          repo_info[head_branch_name]['scan_error_message'],
                          repo_info[head_branch_name]['comparison_status'],
                          repo_info[head_branch_name]['comparison_error_message'],
                          repo_info[head_branch_name]['unique_flows'],
                          repo_info[head_branch_name]['code_scan_time'],
                          repo_info[head_branch_name]['binary_file_size']])

    workbook.save(workbook_location)


def write_summary_data(workbook_location, base_branch_name, head_branch_name, report):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    worksheet = workbook['summary']

    worksheet.append(["Repo", "scan status", f"{base_branch_name} Scan status (ms)", f"{head_branch_name} scan time (ms)",
                      "scan time diff (ms)", "Reachable by flow diff (ms)", f"{base_branch_name} unique flows",
                      f"{head_branch_name} unique flows", "unique flows diff",
                      f"{base_branch_name} No of data elements",
                      f"{head_branch_name} No of data elements", "Data element diff",
                      f"Missing sinks in {head_branch_name}",
                      "No of 100% missing source to sink combinations"])

    for repo in report.keys():
        scan_status = 'done' if report[repo][head_branch_name]['comparison_error_message'] == '--' and report[repo][base_branch_name]['comparison_error_message'] == '--' else 'failed'
        head_scan_time = report[repo][head_branch_name]['code_scan_time'].split()[0]
        base_scan_time = report[repo][base_branch_name]['code_scan_time'].split()[0]

        scan_time_diff = '--' if base_scan_time == '--' or head_scan_time == '--' else int(base_scan_time) - int(head_scan_time)
        unique_flow_diff = '--' if report[repo][base_branch_name]['unique_flows'] == '--' or report[repo][head_branch_name]['unique_flows'] == '--' else int(report[repo][base_branch_name]['unique_flows']) - int(report[repo][head_branch_name]['unique_flows'])
        unique_source_diff = '--' if report[repo][base_branch_name]['unique_source'] == '--' or report[repo][head_branch_name]['unique_source'] == '--' else int(report[repo][base_branch_name]['unique_source']) - int(report[repo][head_branch_name]['unique_source'])
        reachable_flow_time_diff = '--' if report[repo][base_branch_name]['reachable_flow_time'] == '--' or report[repo][head_branch_name]['reachable_flow_time'] == '--' else len(report[repo][base_branch_name]['reachable_flow_time']) - len(report[repo][head_branch_name]['reachable_flow_time'])

        worksheet.append([repo, scan_status, base_scan_time, head_scan_time, scan_time_diff,
                          reachable_flow_time_diff,
                          report[repo][base_branch_name]['unique_flows'],
                          report[repo][head_branch_name]['unique_flows'], unique_flow_diff,
                          report[repo][base_branch_name]['unique_source'],
                          report[repo][head_branch_name]['unique_source'], unique_source_diff,
                          report[repo]['missing_sink'],
                         "---"])

    highlight_summary_cell(worksheet)
    workbook.save(workbook_location)


def highlight_summary_cell(worksheet):

    for col in ['E', 'F', 'I', 'L', 'M']:
        for row in range(2, len(worksheet[col]) + 1):
            if int(worksheet[f'{col}{row}'].value) < 0:
                worksheet[f'{col}{row}'].fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type = "solid")
                worksheet[f'{col}{row}'].font = Font(color='FFFFFF')
            else:
                worksheet[f'{col}{row}'].fill = PatternFill(start_color="90EE90", end_color="90EE90", fill_type="solid")
                worksheet[f'{col}{row}'].font = Font(color='FFFFFF')
