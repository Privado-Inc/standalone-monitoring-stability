import os
import argparse
import re
from math import floor
from pathlib import Path



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
    "missing": "^.*missing\s*(flows|collections|elements|sinks)\.$",
    "additional": "^.*additional\s*(flows|collections|elements)\.$",
    "matching": "^.*matching\s*(flows|collections|elements)\.$",
    "hundred_missing": "^.*hundred.*"
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
    def __init__(self):
        super().__init__()
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, 0, 3)
    def get_summary(self):
        return f'''

        A. Scantime Difference
        {self.more} repos took on an average {self.more_value} ms more.
        {self.less} repos took on an average {self.less_value} ms less.

        '''


class ReachableByFlowTime(TimeDifference):
    def __init__(self):
        super().__init__()
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, 3, 6)
    
    def get_summary(self):
        return f'''
        B. Reachable by flow time difference.
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
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_relevant_data(result):
        number = int(result.split(' ')[0])
        return (number, 0)
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, 6, 10)
    
    def get_summary(self):
        return f'''
        C. Reachable by flow count difference.
        {self.matching} repositories have exactly matching flows.
        {self.less} repositories have missing flows.
        {self.more} repositories have additional flows.
        
        '''
    

class DataElementDifference(Difference):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_relevant_data(result):
        number = int(result.split(' ')[0])
        return (number, 0)
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, 10, 14)

    def get_summary(self):
        return f'''
        D. Unique data elements difference.
        {self.matching} repositories have exactly matching elements.
        {self.less} repositories have missing data elements.
        {self.more} repositories have additional elements.
        
        '''


class MissingSinksVal(Difference):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_relevant_data(result):
        split_data = result.split(" ")
        number = int(split_data[0])
        value = int(split_data[6])
        return (number, value)
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, 14, 16)
    
    def get_summary(self):
        return f'''
        E. Missing sinks.
        {self.less} repositories have on an average {self.less_value} missing sinks.
        
        '''

class SourceToSinkFlowDifference(FlowCollectionDifference):
    def __init__(self):
        super().__init__()
    

    def get_result(self, language_summary):
        return self.diff_pass(language_summary, 16, 21)
    
    def get_summary(self):
        return f'''
        F. Source to Sink Flow data
        {self.hundred_missing} repositories have hundred percent missing flows.
        {self.matching} repositories have exactly matching flows.
        {self.less} repositories have on an average {self.less_value} missing flows.
        {self.more} repositories have on an average {self.more_value} additional flows.
        
        '''

class CollectionDifference(FlowCollectionDifference):
    def __init__(self):
        super().__init__()
    
    def get_result(self, language_summary):
        return self.diff_pass(language_summary, -4)
    
    def get_summary(self):
        return f'''
        G. Collection Summary
        {self.matching} repositories have exactly matching collections.
        {self.less} repositories have missing collections.
        {self.more} repositories have additional collections.
        '''


parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("-s", "--summary-dir")

args: argparse.Namespace = parser.parse_args()

def get_file_contents(summary_dir):
    files = list(Path(summary_dir).rglob("*.[tT][xX][tT]"))
    for f in files:
        with open(f) as content:
            yield list(filter(lambda y: len(y) > 0, map(lambda x: x.strip(), content.readlines())))



def write_summary_to_file(summary,filename="global_summary.txt"):
    with open(filename, "w") as f:
        f.write(summary)


def main():
    scantime_result = ScanTime()
    reachable_by_flow_time_result = ReachableByFlowTime()
    reachable_by_flow_count_difference_result = ReachableByFlowCountDifference()
    source_to_sink_flow_difference_result = SourceToSinkFlowDifference()
    collections_difference_result = CollectionDifference()
    data_element_difference_result = DataElementDifference()
    missing_sinks_value_result = MissingSinksVal()
    summary = ""

    for language_summary in get_file_contents(args.summary_dir):
        scantime_result.get_result(language_summary)
        reachable_by_flow_time_result.get_result(language_summary)
        reachable_by_flow_count_difference_result.get_result(language_summary)
        data_element_difference_result.get_result(language_summary)
        missing_sinks_value_result.get_result(language_summary)
        source_to_sink_flow_difference_result.get_result(language_summary)
        collections_difference_result.get_result(language_summary)

    summary += scantime_result.get_summary()
    summary += reachable_by_flow_time_result.get_summary()
    summary += reachable_by_flow_count_difference_result.get_summary()
    summary += data_element_difference_result.get_summary()
    summary += missing_sinks_value_result.get_summary()
    summary += source_to_sink_flow_difference_result.get_summary()
    summary += collections_difference_result.get_summary()

    write_summary_to_file(summary)


main()
