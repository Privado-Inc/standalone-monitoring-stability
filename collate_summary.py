import argparse
import re
from pathlib import Path
from utils.write_to_file import add_missing_emoji


class Difference:
    def __init__(self) -> None:
        self.more = 0
        self.less = 0
        self.matching = 0
        self.more_value = 0
        self.less_value = 0
        self.matching_value = 0
        self.hundred_missing = 0
    
    def diff_pass(self, language_summary, start, end=None):
        # print(lan)
        for row in language_summary[start:end]:
            if re.match(pattern_match.get("additional"), row):
                number, value = self.get_relevant_data(row)
                self.more += number
                self.more_value += value
            elif re.match(pattern_match.get("hundred_missing"), row):
                number, value = self.get_relevant_data(row)
                self.hundred_missing += number
            elif re.match(pattern_match.get("missing"), row):
                print(row)
                number, value = self.get_relevant_data(row)
                self.less += number
                self.less_value += value
            elif re.match(pattern_match.get("matching"), row):
                number, value = self.get_relevant_data(row)
                self.matching += number
                self.matching_value += value
        return self.get_average()

    def get_average(self):
        return (
            (self.more, self.more_value),
            (self.less, self.less_value),
            (self.matching, self.matching_value)
        )

pattern_match = {
    "ms_more": "^.*ms\s*more\.$",
    "ms_less": "^.*ms\s*less\.$",
    "missing": "^.*missing\s*(flows|collections|elements|sinks)\..*",
    "additional": "^.*additional\s*(flows|collections|elements)\.$",
    "matching": "^.*matching\s*(flows|collections|elements)\.$",
    "hundred_missing": "^.*hundred.*",
    "repo_failed_number": "^.*failed\.$",
    "repo_failed_list": "^Scan failed for.*$"
}


class TimeDifference(Difference):
    def __init__(self):
        super().__init__()
    

    @staticmethod
    def get_relevant_data(result):
        split_data = result.split(" ")
        return (int(split_data[0]), int(split_data[6]))
    
    def get_average(self):
        return (
            (self.more, self.more_value),
            (self.less, self.less_value)
        )

    def diff_pass(self, language_summary, start, end):
        for row in language_summary[start:end]:
            if re.match(pattern_match.get("ms_more"), row):
                number, time = self.get_relevant_data(row)
                self.more += number
                self.more_value += time
            elif re.match(pattern_match.get("ms_less"), row):
                number, time = self.get_relevant_data(row)
                self.less += number
                self.less_value += time
        return self.get_average()



class ScanTime(TimeDifference):
    def __init__(self, offset):
        super().__init__()
        self.start = 0 + offset
        self.end = self.start + 3
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, self.start, self.end)
    def get_summary(self):
        return f'''

        B. Scantime Difference
        {self.more} repos took on an average {self.more_value} ms more.
        {self.less} repos took on an average {self.less_value} ms less.
        '''


class ReachableByFlowTime(TimeDifference):
    def __init__(self, offset):
        super().__init__()
        self.start = 3 + offset
        self.end = self.start + 4
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, self.start, self.end)
    
    def get_summary(self):
        return f'''
        C. Reachable by flow time difference.
        {self.more} repos took on an average {self.more_value} ms more.
        {self.less} repos took on an average {self.less_value} ms less.
        '''


class FlowCollectionDifference(Difference):
    def __init__(self):
        super().__init__()
    
    @staticmethod
    def get_relevant_data(result):
        split_data = result.split(" ")
        if re.match(pattern_match.get("matching"), result) or re.match(pattern_match.get("hundred_missing"), result):
            return (int(split_data[0]), 0)
        elif (re.match(pattern_match.get("additional"), result)) or (re.match(pattern_match.get("missing"), result)):
            if int(split_data[0]) == 0:
                return (int(split_data[0]), 0)
            return (int(split_data[0]), int(split_data[6]))
        
                

class ReachableByFlowCountDifference(FlowCollectionDifference): 
    def __init__(self, offset): # offset is the location at which the actual summary starts
        super().__init__()
        self.start = 6 + offset
        self.end = self.start + 4

    @staticmethod
    def get_relevant_data(result):
        number = int(result.split(' ')[0])
        return (number, 0)
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, 10, 14)
    
    def get_summary(self):
        return f'''
        D. Reachable by flow count difference.
        {self.matching} repositories have exactly matching flows.
        {self.less} repositories have missing flows. {add_missing_emoji(self.less)}
        {self.more} repositories have additional flows.
        '''
    

class DataElementDifference(Difference):
    def __init__(self, offset):
        super().__init__()
        self.start = 10 + offset
        self.end = self.start + 4

    @staticmethod
    def get_relevant_data(result):
        number = int(result.split(' ')[0])
        return (number, 0)
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, self.start, self.end)

    def get_summary(self):
        return f'''
        E. Unique data elements difference.
        {self.matching} repositories have exactly matching elements.
        {self.less} repositories have missing data elements. {add_missing_emoji(self.less)}
        {self.more} repositories have additional elements.
        '''


class MissingSinksVal(Difference):
    def __init__(self, offset):
        super().__init__()
        self.start = 14 + offset
        self.end = self.start + 2

    @staticmethod
    def get_relevant_data(result):
        split_data = result.split(" ")
        number = int(split_data[0])
        value = int(split_data[6])
        return (number, value)
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, self.start, self.end)
    
    def get_summary(self):
        return f'''
        F. Missing sinks.
        {self.less} repositories have on an average {self.less_value} missing sinks. {add_missing_emoji(self.less)}
        '''

class SourceToSinkFlowDifference(FlowCollectionDifference):
    def __init__(self, offset):
        super().__init__()
        self.start = 16 + offset
        self.end = self.start + 5
    

    def get_result(self, language_summary):
        return self.diff_pass(language_summary, self.start, self.end)
    
    def get_summary(self):
        return f'''
        G. Source to Sink Flow data
        {self.hundred_missing} repositories have hundred percent missing flows. {add_missing_emoji(self.hundred_missing)} {add_missing_emoji(self.hundred_missing)}
        {self.matching} repositories have exactly matching flows.
        {self.less} repositories have on an average {self.less_value} missing flows. {add_missing_emoji(self.less)}
        {self.more} repositories have on an average {self.more_value} additional flows.
        '''

class CollectionDifference(FlowCollectionDifference):
    def __init__(self, offset):
        super().__init__()
        self.start = 21 + offset
        self.end = self.start + 4
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, self.start, self.end)
    
    def get_summary(self):
        return f'''
        H. Collection Summary
        {self.matching} repositories have exactly matching collections.
        {self.less} repositories have missing collections. {add_missing_emoji(self.less)}
        {self.more} repositories have additional collections.
        '''

class ScanFailureReport():
    def __init__(self, offset, end):
        self.num_repos_failed = 0
        self.repos_failed = ""
        self.total_repos = 0
        self.end = end
    
    def get_number_repos_failed(self, language_summary):
        for row in language_summary[0:3]:
            if re.match(pattern_match.get("repo_failed_number"), row):
                line = row.split(" ")
                self.num_repos_failed += int(line[2])
                self.total_repos += int(line[-3])
    
    def get_repo_name_failed(self, language_summary):
        for i, row in enumerate(language_summary[0:self.end]):
            if re.match(pattern_match.get("repo_failed_list"), row):
                self.repos_failed += f"{row}"
                if i < self.end - 1:
                    self.repos_failed += "\n\t"

    def get_result(self, language_summary):
        self.get_number_repos_failed(language_summary)
        self.get_repo_name_failed(language_summary)

    def get_summary(self):
        return f'''
        A. Repository scan failure report
        Scan for {self.num_repos_failed} repositories out of {self.total_repos} failed. {":rotating_light:" if self.num_repos_failed > 0 else ""}
        {self.repos_failed}'''

    


parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("-s", "--summary-dir")

args: argparse.Namespace = parser.parse_args()

def get_file_contents(summary_dir):
    files = list(Path(summary_dir).rglob("*.[tT][xX][tT]"))
    for f in files:
        with open(f) as content:
            yield list(filter(lambda y: len(y) > 0, map(lambda x: x.strip(), content.readlines())))



def get_num_until_summary_start(language_summary):
    for i, row in enumerate(language_summary):
        if re.match("^B\..*$", row):
            return i
    return -1

def write_summary_to_file(summary,filename="global_summary.txt"):
    with open(filename, "w") as f:
        f.write(summary)


def main():
    scanfail_report = ScanFailureReport(0,-1)
    scantime_result = ScanTime(0)
    reachable_by_flow_time_result = ReachableByFlowTime(0)
    reachable_by_flow_count_difference_result = ReachableByFlowCountDifference(0)
    source_to_sink_flow_difference_result = SourceToSinkFlowDifference(0)
    collections_difference_result = CollectionDifference(0)
    data_element_difference_result = DataElementDifference(0)
    missing_sinks_value_result = MissingSinksVal(0)
    summary = ""


    for language_summary in get_file_contents(args.summary_dir):
        scantime_start = get_num_until_summary_start(language_summary)
       
        scanfail_report = ScanFailureReport(0, scantime_start)
        scanfail_report.get_result(language_summary)
        
        scantime_result = ScanTime(scantime_start)
        scantime_result.get_result(language_summary)

        reachable_by_flow_time_result = ReachableByFlowTime(scantime_start)
        reachable_by_flow_time_result.get_result(language_summary)

        reachable_by_flow_count_difference_result = ReachableByFlowCountDifference(scantime_start)
        reachable_by_flow_count_difference_result.get_result(language_summary)

        source_to_sink_flow_difference_result = SourceToSinkFlowDifference(scantime_start)
        source_to_sink_flow_difference_result.get_result(language_summary)

        collections_difference_result = CollectionDifference(scantime_start)
        collections_difference_result.get_result(language_summary)

        data_element_difference_result = DataElementDifference(scantime_start)
        data_element_difference_result.get_result(language_summary)

        missing_sinks_value_result = MissingSinksVal(scantime_start)
        missing_sinks_value_result.get_result(language_summary)

    summary += scanfail_report.get_summary()
    summary += scantime_result.get_summary()
    summary += reachable_by_flow_time_result.get_summary()
    summary += reachable_by_flow_count_difference_result.get_summary()
    summary += data_element_difference_result.get_summary()
    summary += missing_sinks_value_result.get_summary()
    summary += source_to_sink_flow_difference_result.get_summary()
    summary += collections_difference_result.get_summary()

    write_summary_to_file(summary)


main()
