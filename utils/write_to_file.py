import csv
import os

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

