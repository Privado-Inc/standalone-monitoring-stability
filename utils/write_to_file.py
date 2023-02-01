import csv
import os
import openpyxl


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


def create_new_excel(location, base_branch_name, head_branch_name):
    wb = openpyxl.Workbook()
    # Delete the default sheet
    wb.remove(wb.active)
    # Create new Sheet
    wb.create_sheet(f'{head_branch_name}-{base_branch_name}-source-&-sink-report')
    wb.create_sheet(f'{head_branch_name}-{base_branch_name}-flow-report')
    wb.create_sheet(f'{head_branch_name}-{base_branch_name}-performance-report')
    wb.save(location)


def write_source_sink_data(workbook_location, report, base_branch_name, head_branch_name):
    # load the workbook
    workbook = openpyxl.load_workbook(filename=workbook_location)

    # create new sheet for source-sink-collection sheet
    worksheet = workbook[f'{head_branch_name}-{base_branch_name}-source-&-sink-report']

    for row in report:
        print(row)
        worksheet.append(row)

    workbook.save(workbook_location)


def write_path_data(workbook_location, report, base_branch_name, head_branch_name):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    # create new sheet for source-sink-collection sheet
    worksheet = workbook[f'{head_branch_name}-{base_branch_name}-flow-report']

    for row in report:
        worksheet.append(row)

    workbook.save(workbook_location)


def write_performance_data(workbook_location, report, base_branch_name, head_branch_name):
    workbook = openpyxl.load_workbook(filename=workbook_location)

    # create new sheet for source-sink-collection sheet
    worksheet = workbook[f'{head_branch_name}-{base_branch_name}-performance-report']

    for row in report:
        worksheet.append(row)

    workbook.save(workbook_location)