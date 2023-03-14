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
            if re.search(exclusion_regex, line):
                continue

            separate_by_tag = line.split('-')

            if re.search(binary_filesize_regex, line):
                yield "Binary file size", separate_by_tag[-1]
                continue

            if re.search(source_sink_regex, line):
                yield separate_by_tag[-2], separate_by_tag[-1]
                continue

            if re.search(language_regex, line):
                detected_language = line.split(' ')[-1].replace("'", "")
                yield "language", detected_language
            
            if re.search(time_filter_regex, line):

                empty_filtered_list = list(
                    filter(
                        # because the line is of the form "Tag key - zzMS", remove all the spaces and tabs
                        lambda x: not re.match(r"^\s+$", x) and len(x), separate_by_tag))
                # Only consider the tag names and time required, Ex - Language Detection done in and ZZms
                tag_time_pair = empty_filtered_list[1:]

                # Generate output for each line
                yield tuple(tag_time_pair)


def get_subscan_metadata(repo_name, branch, branch_file_name, language):
    subscan_map = dict()
    cwd = os.getcwd()
    filepath = f"{cwd}/temp/result/{branch_file_name}/{repo_name}-output.txt"

    subscan_map["RepoName"] = repo_name
    subscan_map["language"] = language
    subscan_map["branch"] = branch

    missing_in_python_regex = r".*(Property file pass|IdentifierTagger Non Member|DBConfigTagger|CustomInheritTagger).*"

    missing_in_python_values = dict()

    for metadata_pair in get_metadata_pair(filepath):
        tag = re.sub(pattern=r"(\t|done in|is done in)", repl="", string=metadata_pair[0]).strip()
        # base processing is the cpg generation time
        if "Base processing" in tag:
            tag = "CPG Generation time"
        
        time = metadata_pair[1].strip()
        flow_count = int(metadata_pair[-1].replace('\n', '').strip()) if metadata_pair[-1].replace('\n', '').strip().isdigit() and "flow" in metadata_pair[0] else None # Time required and flow count both are captured 
        
        # Store values for java to avoid mismatch of values
        if re.search(r".*(Java).*", language):
            if re.search(missing_in_python_regex, tag):
                missing_in_python_values[tag] = time
                continue

        # Map all the tags to the times in a dictionary
        subscan_map[tag] = time

        if flow_count is not None:
            # Changing key to avoid confusion between flow counts and time required for flow counts, and also to
            # prevent overrides
            subscan_map[tag + " (time) "] = time
            subscan_map[tag] = flow_count

    # Moved down to sync values with headers
    if re.search(r".*(Java).*", language):
        subscan_map["Property file pass"] = missing_in_python_values["Property file pass"]
        if missing_in_python_values.__contains__("IdentifierTagger Non Member"):
            subscan_map["IdentifierTagger Non Member"] = missing_in_python_values["IdentifierTagger Non Member"]
        else:
            subscan_map["IdentifierTagger Non Member"] = 'NA'
        subscan_map["DB config tagger"] = missing_in_python_values["DBConfigTagger"]
        subscan_map["Custom Inherit Tagger"] = missing_in_python_values["CustomInheritTagger"]
        subscan_map['RegularSinkTagger'], subscan_map['APITagger'] = subscan_map['APITagger'], subscan_map['RegularSinkTagger'] # Hot fix for java

    # Missing in python should be added at the end
    if re.search(r".*(Python).*", language):
        subscan_map["Property file pass"] = "--"
        subscan_map["IdentifierTagger Non Member"] = "--"
        subscan_map["DB config tagger"] = "--"
        subscan_map["Custom Inherit Tagger"] = "--"

    return subscan_map


