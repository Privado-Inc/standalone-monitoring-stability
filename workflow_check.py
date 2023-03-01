import re
import sys
import os


def main(filepath):

    scan_time_regex = r".*(repos took an average).*(ms more).*"

    reachable_regex = r".*(repositories have missing flows.).*"

    data_element_regex = r".*(repositories have missing data elements.).*"

    sink_regex = r".*(repositories have an average).*(missing sinks.).*"

    source_sink_regex = r".*(repositories have on an average).*(missing flows.).*"

    results = []

    check = True

    with open(filepath) as summary_report:

        for line in summary_report.readlines():

            print(line)

            if re.search(scan_time_regex, line) and check:
                values = line.split(" ")
                print(values)
                check = False
                if int(values[-3]) > 1000:
                    results.append("Average scan time differance more than 1000 ms")

            if re.search(reachable_regex, line):
                values = line.split(" ")
                if int(values[-5]) != 0:
                    results.append("Missing Reachable by flow Detected")

            if re.search(data_element_regex, line):
                values = line.split(" ")
                if int(values[-6]) != 0:
                    results.append("Missing Data Element Detected")

            if re.search(sink_regex, line):
                values = line.split(" ")
                if int(values[-8]) != 0 or int(values[-3]) != 0:
                    results.append("Missing Sink Detected")

            if re.search(source_sink_regex, line):
                values = line.split(" ")
                if int(values[-9]) != 0 or int(values[-3]) != 0:
                    results.append("Source to sink flow missing Detected")

        output_path = f'{os.getcwd()}/action_result.txt'

        if os.path.isfile(output_path):
            os.system(f'rm {output_path}')

        file = open(output_path, 'w')

        if len(results) == 0:
            file.write("true")
        else:
            file.writelines('\n'.join(results))

        file.close()


if __name__ == '__main__':
    summary_path = sys.argv[1]
    main(summary_path)