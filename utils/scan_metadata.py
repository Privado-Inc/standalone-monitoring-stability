import os
import re




def get_metadata_pair(filepath):
    # Match all lines which contain WWh:XXm:YYs:ZZZms
    time_filter_regex = r".*(\d{1,2}h:\d{1,2}m:\d{1,2}s:\d{1,3}ms).*"

    # Match number of source and sink nodes
    source_sink_regex = r".*(no of source nodes|no of sinks nodes).*"

    # Match line which contains binary file size 
    binary_filesize_regex = r".*(Binary file size).*"

    # Lines which need to be excluded
    exclusion_regex = r".*(Lombok).*"

    language_regex = r".*(Detected language).*"

    with open(filepath) as scan_time_output:
        for line in scan_time_output.readlines():
            if (re.search(exclusion_regex, line)):
                continue

            separate_by_tag = line.split('-')

            if (re.search(binary_filesize_regex, line)):
                yield ("Binary file size", separate_by_tag[-1])
                continue

            if (re.search(source_sink_regex, line)):
                yield (separate_by_tag[-2], separate_by_tag[-1])
                continue

            if (re.search(language_regex, line)):
                detected_language = line.split(' ')[-1].replace("'", "")
                yield ("language", detected_language)    
            
            if (re.search(time_filter_regex, line)):

                empty_filtered_list = list(
                    filter(
                        lambda x: not re.match(r"^\s+$", x) and len(x), separate_by_tag)) # because the line is of the form "Tag key - zzMS", remove all the spaces and tabs

                tag_time_pair = empty_filtered_list[1:] # Only consider the tag names and time required, Ex - Language Detection done in and ZZms


                yield tuple(tag_time_pair) # Generate output for each line


def get_subscan_metadata(repo_name, branch, language):
    subscan_map = dict()
    cwd = os.getcwd()
    filepath = f"{cwd}/temp/result/{branch}/{repo_name}-output.txt"

    subscan_map["RepoName"] = repo_name
    subscan_map["language"] = language
    subscan_map["branch"] = branch

    missing_in_python_regex = r".*(Property file pass|IdentifierTagger Non Member|DB config tagger).*"

    missing_in_python_values = dict()
    

    for metadata_pair in get_metadata_pair(filepath):
        tag = re.sub(pattern=r"(\t|done in|is done in)",repl="", string=metadata_pair[0]).strip()
        if ("Base processing" in tag): # base processing is the cpg generation time
            tag = "CPG Generation time"
        
        time = metadata_pair[1].strip()

        flow_count = int(metadata_pair[-1].replace('\n', '').strip()) if metadata_pair[-1].replace('\n', '').strip().isdigit() and "flow" in metadata_pair[0] else None # Time required and flow count both are captured 
        
        if (re.search(r".*(Java).*", language)):
            if (re.search(missing_in_python_regex, tag)):
                print("Missing in python")
                missing_in_python_values[tag] = time
            

        subscan_map[tag] = time # Map all the tags to the times in a dictionary
        

        if (flow_count is not None):
            subscan_map[tag + " (time) "] = time # Changing key to avoid confusion between flow counts and time required for flow counts, and also to prevent overrides
            subscan_map[tag] = flow_count
    
    if (re.search(r".*(Java).*", language)):
        subscan_map["Property file pass"] = missing_in_python_values["Property file pass"]
        subscan_map["IdentifierTagger Non Member"] = missing_in_python_values["IdentifierTagger Non Member"]
        subscan_map["DB config tagger"] = missing_in_python_values["DB config tagger"]

    if (re.search(r".*(Python).*", language)):
        subscan_map["Property file pass"] = "--"
        subscan_map["IdentifierTagger Non Member(ms)"] = "--"
        subscan_map["DB config tagger"] = "--"

    return subscan_map


# (' Language detection done in \t\t\t', ' 17 ms ', ' 00h:00m:00s:17ms\n')
# ('language', 'Python\n')
# (' Base processing done in \t\t\t\t', ' 2712 ms ', ' 00h:00m:02s:712ms\n')
# (' Run oss data flow is done in \t\t\t', ' 1 ms ', ' 00h:00m:00s:01ms\n')
# ('LiteralTagger is done in \t\t\t', ' 283 ms ', ' 00h:00m:00s:283ms\n')
# ('IdentifierTagger is done in \t\t\t', ' 1436 ms ', ' 00h:00m:01s:436ms\n')
# ('APITagger is done in \t\t\t', ' 237 ms ', ' 00h:00m:00s:237ms\n')
# ('RegularSinkTagger is done in \t\t\t', ' 2938 ms ', ' 00h:00m:02s:938ms\n')
# ('CollectionTagger is done in \t\t\t', ' 17 ms ', ' 00h:00m:00s:17ms\n')
# (' Tagging source code is done in \t\t\t', ' 10905 ms ', ' 00h:00m:10s:905ms\n')
# ('no of source nodes ', ' 151\n')
# ('no of sinks nodes ', ' 2140\n')
# ('Finding flows is done in \t\t\t', ' 497 ms ', ' 00h:00m:00s:497ms ', ' Unique flows ', ' 203\n')
# ('Filtering flows 1 is done in \t\t\t', ' 16 ms ', ' 00h:00m:00s:16ms ', ' Unique flows ', ' 203\n')
# ('Filtering flows 2 is done in \t\t\t', ' 46 ms ', ' 00h:00m:00s:46ms ', ' Final flows ', ' 197\n')
# ('Deduplicating flows is done in \t\t', ' 19 ms ', ' 00h:00m:00s:19ms ', ' Unique flows ', ' 89\n')
# (' Finding source to sink flow is done in \t\t', ' 997 ms ', ' 00h:00m:00s:997ms ', ' Processed final flows ', ' 89\n')
# (' Code scanning is done in \t\t\t', ' 14633 ms ', ' 00h:00m:14s:633ms\n')
# ('Binary file size', ' 0.004096 MB\n')


