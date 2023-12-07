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
            print("\t--------------- 1")
            if re.search(exclusion_regex, line):
                continue
            
            print("\t----------------- 2")
            separate_by_tag = line.split('-')

            if re.search(binary_filesize_regex, line):
                yield "Binary file size", separate_by_tag[-1]
                continue
            print("\t----------------- 3")
            if re.search(source_sink_regex, line):
                yield separate_by_tag[-2], separate_by_tag[-1]
                continue
            
            print("\t----------------- 4")
            if re.search(language_regex, line):
                detected_language = line.split(' ')[-1].replace("'", "")
                yield "language", detected_language
            
            print("\t----------------- 5")
            if re.search(time_filter_regex, line):
                print("\t----------------- 6")
                empty_filtered_list = list(
                    filter(
                        # because the line is of the form "Tag key - zzMS", remove all the spaces and tabs
                        lambda x: not re.match(r"^\s+$", x) and len(x), separate_by_tag))
                print("\t-----------------7")
                # Only consider the tag names and time required, Ex - Language Detection done in and ZZms
                tag_time_pair = empty_filtered_list[1:]
                print("\t----------------- 8")

                # Generate output for each line
                yield tuple(tag_time_pair)


def get_subscan_metadata(repo_name, branch, branch_file_name, language):
    subscan_map = dict()
    cwd = os.getcwd()
    filepath = f"{cwd}/temp/result/{branch_file_name}/{repo_name}-output.txt"


    try:
        subscan_map["RepoName"] = repo_name
        subscan_map["language"] = language
        subscan_map["branch"] = branch

        missing_in_python_regex = r".*(Property file pass|IdentifierTagger Non Member|DBConfigTagger|CustomInheritTagger).*"

        missing_in_python_values = dict()

        print("step 1")
        for metadata_pair in get_metadata_pair(filepath):
            print("step 1.1")
            print(metadata_pair)
            tag = re.sub(pattern=r"(\t|done in|is done in)", repl="", string=metadata_pair[0]).strip()
            # base processing is the cpg generation time
            print("step 1.2")
            if "Base processing" in tag:
                tag = "CPG Generation time"
            
            time = metadata_pair[1].strip()
            flow_count = int(metadata_pair[-1].replace('\n', '').strip()) if metadata_pair[-1].replace('\n', '').strip().isdigit() and "flow" in metadata_pair[0] else None # Time required and flow count both are captured 
            print("step 1.3")
            # Store values for java to avoid mismatch of values
            if re.search(r".*(Java).*", language):
                print("step 1.3.1")
                if re.search(missing_in_python_regex, tag):
                    print("step 1.3.1.1")
                    missing_in_python_values[tag] = time
                    continue

            # Map all the tags to the times in a dictionary
            subscan_map[tag] = time
        
            if flow_count is not None:
                # Changing key to avoid confusion between flow counts and time required for flow counts, and also to
                # prevent overrides
                subscan_map[tag + " (time) "] = time
                subscan_map[tag] = flow_count

        print("step 2")
        # Moved down to sync values with headers
        if re.search(r".*(Java).*", language):
            print("step 2.1")
            subscan_map["Property file pass"] = missing_in_python_values["Property file pass"]
            print("step 2.2")

            subscan_map["IdentifierTagger Non Member"] = missing_in_python_values["IdentifierTagger Non Member"]
            print("step 2.3")

            subscan_map["DB config tagger"] = missing_in_python_values["DBConfigTagger"]
            print("step 2.4")
            subscan_map["Custom Inherit Tagger"] = missing_in_python_values["CustomInheritTagger"]
            print("step 2.5")

            subscan_map['RegularSinkTagger'], subscan_map['APITagger'] = subscan_map['APITagger'], subscan_map['RegularSinkTagger'] # Hot fix for java
            print("step 2.6 ")

        print("step 3")
        # Missing in python should be added at the end
        if re.search(r".*(Python).*", language):
            print("step 3.1")
            subscan_map["Property file pass"] = "--"
            subscan_map["IdentifierTagger Non Member"] = "--"
            subscan_map["DB config tagger"] = "--"
            subscan_map["Custom Inherit Tagger"] = "--"
    except Exception as e:
        print(e)

    return subscan_map


