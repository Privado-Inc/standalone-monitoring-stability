import csv
import os

def write_to_csv(filename, headers, values):
    # filename is the name of the granular report
    # headers is an array containing the column names -
    # values is a 2D Array with each element signifying a particular row
    cwd = os.getcwd()
    with open(f'{cwd}/{filename}.csv', "a") as value:
        report = csv.writer(value)
        report.writerow(headers)
        for row in values:
            report.writerow(row)

