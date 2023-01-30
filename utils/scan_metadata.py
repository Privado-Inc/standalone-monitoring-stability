import os
import re

def get_metadata_pair(filepath):
    # Match all lines which contain WWh:XXm:YYs:ZZZms
    time_filter_regex = r".*(\d{1,2}h:\d{1,2}m:\d{1,2}s:\d{1,3}ms).*"

    # Match number of source and sink nodes
    source_sink_regex = r".*(no of source nodes|no of sink nodes).*"

    # Match line which contains binary file size 
    binary_filesize_regex = r".*(Binary file size).*"

    with open(filepath) as scan_time_output:
        for line in scan_time_output.readlines():
            separate_by_tag = line.split('-')

            if (re.search(binary_filesize_regex, line)):
                yield ["Binary file size", separate_by_tag[-1]]
                continue

            if (re.search(source_sink_regex, line)):
                yield [separate_by_tag[-2], separate_by_tag[-1]]
                continue
                
            if (re.search(time_filter_regex, line)):

                empty_filtered_list = list(
                    filter(
                        lambda x: not re.match(r"^\s+$", x) and len(x), separate_by_tag)) # because the line is of the form "Tag key - zzMS", remove all the spaces and tabs

                tag_time_pair = empty_filtered_list[1:] # Only consider the tag names and time required, Ex - Language Detection done in and ZZms


                yield tuple(tag_time_pair) # Generate output for each line


def get_subscan_metadata(repo_name, branch):
    subscan_map = dict()
    cwd = os.getcwd()
    filepath = f"{cwd}/temp/result/{branch}/{repo_name}-output.txt"

    subscan_map["RepoName"] = repo_name
    subscan_map["branch"] = branch

    for metadata_pair in get_metadata_pair(filepath):
        print(metadata_pair)
        tag = re.sub(pattern=r"(\t|done in|is done in)",repl="", string=metadata_pair[0]).strip()
        if ("Base processing" in tag): # base processing is the cpg generation time
            tag = "CPG Generation time"
        
        time = metadata_pair[1].strip()

        flow_count = int(metadata_pair[-1].replace('\n', '').strip()) if metadata_pair[-1].replace('\n', '').strip().isdigit() and "flow" in metadata_pair[0] else None # Time required and flow count both are captured 
        
        subscan_map[tag] = time # Map all the tags to the times in a dictionary
        
        if (flow_count is not None):
            subscan_map[tag + " (time) "] = time # Changing key to avoid confusion between flow counts and time required for flow counts, and also to prevent overrides
            subscan_map[tag] = flow_count
    
    return subscan_map
