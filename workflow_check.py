import re
import sys
import os


def main(filepath):

    scan_time_regex = r".*(repos took an average).*(ms more).*"

    reachable_regex = r".*(repositories have missing flows.).*"

    data_element_regex = r".*(repositories have missing data elements.).*"

    sink_regex = r".*(repositories have on an average).*(missing sinks.).*"

    source_sink_regex = r".*(repositories have hundred percent missing flows.).*"

    collection_regex = r".*(repositories have missing collections).*"

    scan_time_limit = 60000

    results = []

    check = True

    with open(filepath, "r+") as summary_report:

        for line in summary_report.readlines():

            print(line)
            values = list(filter(lambda y: len(y) > 0, map(lambda x: x.strip(), line.split(" "))))
            if re.search(scan_time_regex, line) and check:
                # values = line.split(" ")
                print(values)
                check = False
                if int(values[-3]) > scan_time_limit:
                    results.append("Average scan time differance more than 1000 ms")

            if re.search(reachable_regex, line):
                # values = line.split(" ")
                if int(values[0]) != 0:
                    results.append("Missing Reachable by flow Detected")

            if re.search(data_element_regex, line):
                # values = line.split(" ")
                if int(values[0]) != 0:
                    results.append("Missing Data Element Detected")

            if re.search(sink_regex, line):
                # values = line.split(" ")
                if int(values[0]) != 0:
                    results.append("Missing Sink Detected")

            if re.search(source_sink_regex, line):
                # values = line.split(" ")
                if int(values[0]) != 0:
                    results.append("Source to sink flow missing Detected")

            if (re.search(collection_regex, line)):
                # values = line.split(" ")
                if (int(values[0]) != 0):
                    results.append("Missing collections detected")


        output_path = f'{os.getcwd()}/action_result.txt'

        file = open(output_path, 'a')

        if len(results) == 0:
            file.write("true")
        else:
            file.writelines('\n'.join(results))

        file.close()


if __name__ == '__main__':
    summary_path = sys.argv[1]
    main(summary_path)