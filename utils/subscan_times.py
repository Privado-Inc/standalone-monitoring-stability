import os
import re

def get_tag_time_pairs(filepath):
    # Match all lines which contain WWh:XXm:YYs:ZZZms
    time_filter_regex = r".*(\d{1,2}h:\d{1,2}m:\d{1,2}s:\d{1,3}ms).*"

    # Match line which contains binary file size 
    binary_filesize_regex = r".*(Binary file size).*"

    with open(filepath) as scan_time_output:
        for line in scan_time_output.readlines():
            if (re.search(time_filter_regex, line)):

                tag_separated_list = list(
                    filter(
                        lambda x: not re.match(r"^\s+$", x) and len(x), line.split('-'))) # because the line is of the form "Tag key - zzMS", remove all the spaces and tabs

                tag_time_pair = tag_separated_list[1:3] # Only consider the tag names and time required, Ex - Language Detection done in and ZZms

                
                yield tuple(tag_time_pair) # Generate output for each line


def get_subscan_times(branch):
    subscan_map = dict()
    filepath = f"{cwd}/temp/result/{branch}/output.txt"

    for tag_time_pair in get_tag_time_pairs(filepath):
        tag = re.sub(pattern=r"(\t|done in|is done in)",repl="", string=tag_time_pair[0]).strip()
        time = tag_time_pair[1].strip() 
        subscan_map[tag] = time # Map all the tags to the times in a dictionary
    
    return subscan_map
    
