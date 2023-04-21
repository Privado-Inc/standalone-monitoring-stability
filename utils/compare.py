import csv
import json
import os
import hashlib
import builder
import config
from utils.write_to_file import write_source_sink_data, write_path_data, write_performance_data, write_scan_status_report_for_file
from utils.scan_metadata import get_subscan_metadata
from utils.scan import generate_scan_status_data_for_file


def main(base_file, head_file, base_intermediate_file, head_intermediate_file, header_flag, scan_status, language):
    try:
        base_file.split('/')[-1].split('.')[0]
    except Exception as e:
        print(f'{builder.get_current_time()} - Please enter a valid file: {e}')
        return

    base_file = open(base_file)
    head_file = open(head_file)

    base_data = json.load(base_file)
    head_data = json.load(head_file)

    repo_name = base_data['repoName']

    head_branch_worksheet_name = config.HEAD_SHEET_BRANCH_NAME.replace('/', '-')
    base_branch_worksheet_name = config.BASE_SHEET_BRANCH_NAME.replace('/', '-')

    process_source_sink_and_collection_data(f'{head_branch_worksheet_name}-{base_branch_worksheet_name}-source-&-sink-report',
                                            base_data, head_data, repo_name,
                                            header_flag, scan_status, language)

    process_path_analysis(f'{head_branch_worksheet_name}-{base_branch_worksheet_name}-flow-report', base_data,
                          head_data, repo_name, language, header_flag)

    process_collection_sheet_data(f'{head_branch_worksheet_name}-{base_branch_worksheet_name}-collections-report',
                                  base_data, head_data, repo_name, language, header_flag, True)

    if os.path.isfile(base_intermediate_file) and os.path.isfile(head_intermediate_file):
        base_intermediate_file = open(base_intermediate_file)
        head_intermediate_file = open(head_intermediate_file)

        base_intermediate_data = json.load(base_intermediate_file)
        head_intermediate_data = json.load(head_intermediate_file)

        process_unique_path_analysis(f'{head_branch_worksheet_name}-{base_branch_worksheet_name}-unique-flow-report',
                                     base_intermediate_data, head_intermediate_data, repo_name, header_flag, language)

        base_intermediate_file.close()
        head_intermediate_file.close()

    process_performance_data(f'{head_branch_worksheet_name}-{base_branch_worksheet_name}-performance-report', repo_name,
                             language, header_flag)

    base_file.close()
    head_file.close()


# when only need to compare the Privado.json file
def compare_files(base_file_uri, head_file_uri):
    if not os.path.isfile(base_file_uri):
        print(f'{builder.get_current_time()} - Please provide complete valid base file: {base_file_uri}')
        return

    if not os.path.isfile(head_file_uri):
        print(f'{builder.get_current_time()} - Please provide complete valid head file: {head_file_uri}')
        return

    base_file = open(base_file_uri)
    head_file = open(head_file_uri)
    base_data = json.load(base_file)
    head_data = json.load(head_file)

    first_repo_name = base_data['repoName']
    second_repo_name = head_data['repoName']

    # initialize the repo name only when both name are same
    repo_name = first_repo_name if first_repo_name == second_repo_name else 'NA'

    status_report_data = generate_scan_status_data_for_file(repo_name, base_file_uri, head_file_uri)
    write_scan_status_report_for_file(f'{os.getcwd()}/output.xlsx', "First", "Second", status_report_data)

    process_source_sink_and_collection_data('source-&-sink-report', base_data, head_data, repo_name,
                                            True, None, None)

    process_path_analysis('flow-report', base_data, head_data, repo_name, "NA", True, True)

    base_file.close()
    head_file.close()


def process_performance_data(worksheet_name, repo_name, language, header_flag):
    result = []
    subscan_headers = list(get_subscan_metadata(repo_name, config.HEAD_CORE_BRANCH_NAME, config.HEAD_CORE_BRANCH_KEY,
                                                language).keys())
    if header_flag:
        result.append(subscan_headers)
    else:
        result.append([])

    head_values = get_subscan_metadata(repo_name, config.BASE_CORE_BRANCH_NAME, config.BASE_CORE_BRANCH_KEY, language)
    base_values = get_subscan_metadata(repo_name, config.HEAD_CORE_BRANCH_NAME, config.HEAD_CORE_BRANCH_KEY, language)

    result.append(list(map(lambda x: head_values.get(x, "--"), subscan_headers)))
    result.append(list(map(lambda x: base_values.get(x, "--"), subscan_headers)))

    write_performance_data(f'{os.getcwd()}/output.xlsx', worksheet_name, result)


def top_level_collection_processor(collections_base, collections_head, repo_name, language):
    report = []
    for collection in list(zip(collections_base, collections_head)):
        report.append(
            process_collection(collection[0], collection[1], collection[0]['name'], repo_name, language))

    return report


def process_collection(collections_base, collections_head, collection_name, repo_name, language):
    result = []
    base_collections = len(collections_base['collections'])
    head_collections = len(collections_head['collections'])

    collections_sources_base = []
    collections_sources_head = []

    for ci in collections_base['collections']:
        collections_sources_base.append(ci['sourceId'])

    for ci in collections_head['collections']:
        collections_sources_head.append(ci['sourceId'])

    collection_set_base = set(collections_sources_base)
    collection_set_head = set(collections_sources_head)

    latest = '\n'.join(list(collection_set_head.difference(collection_set_base)))
    removed = '\n'.join(list(collection_set_base.difference(collection_set_head)))

    collections_sources_base = '\n'.join(collections_sources_base)
    collections_sources_head = '\n'.join(collections_sources_head)

    # No of nodes in base, but not in head
    missing_head = len(collection_set_base.union(collection_set_head).difference(collection_set_head))

    return [repo_name, language, 'Collection', collection_name, head_collections, base_collections,
            collections_sources_head, collections_sources_base, '0', latest, removed, missing_head]


def create_csv(data):
    cwd = os.getcwd()
    with open(f'{cwd}/comparison_report.csv', "a") as value:
        report = csv.writer(value)
        for i in data:
            report.writerow(i)

    print(f'{builder.get_current_time()} - Report written and exported to: {cwd}/comparison_report.csv')


def process_source_sink_and_collection_data(worksheet_name, base_data, head_data, repo_name, header_flag, scan_status,
                                            language):
    result = []

    if header_flag:
        result.append(['Repo', 'language', 'Category', 'Sub Category',
                       f'Number of Node ( {config.HEAD_SHEET_BRANCH_NAME} )',
                       f'Number of Node ( {config.BASE_SHEET_BRANCH_NAME} )',
                       f'List of Node {config.HEAD_SHEET_BRANCH_NAME}',
                       f'List of Node {config.HEAD_SHEET_BRANCH_NAME}',
                       '% Change', f'New Node added in {config.HEAD_SHEET_BRANCH_NAME}',
                       f'List of Node Missing in {config.HEAD_SHEET_BRANCH_NAME}',
                       f'Number of missing nodes in {config.HEAD_SHEET_BRANCH_NAME}'])

    # Analysis for the Source
    result.append(process_sources(base_data['sources'], head_data['sources'], repo_name, language))
    # Analysis for the storages sink
    result.append(process_sinks(base_data['dataFlow'], head_data['dataFlow'], repo_name, scan_status, language,
                                key='storages'))
    # Analysis for the third party sink
    result.append(process_sinks(base_data['dataFlow'], head_data['dataFlow'], repo_name, scan_status, language,
                                key='third_parties'))
    # Analysis for the leakage sink
    result.append(process_sinks(base_data['dataFlow'], head_data['dataFlow'], repo_name, scan_status, language,
                                key='leakages'))
    # Analysis for the collections
    for row in top_level_collection_processor(base_data['collections'], head_data['collections'], repo_name, language):
        result.append(row)

    # Export the result in new sheet Excel sheet
    write_source_sink_data(f'{os.getcwd()}/output.xlsx', worksheet_name, result)

    return result


def process_collection_sheet_data(worksheet_name, base_collections, head_collections, repo_name, language, header_flag, write_report):
    result = []

    head_total_occ = 0
    base_total_occ = 0
    total_additional_occ = 0
    total_missing_occ = 0

    value = sub_process_occurrences(base_collections['collections'], head_collections['collections'], repo_name, language)

    for i in value[0]:
        result.append(i)

    head_total_occ += value[1][0]
    base_total_occ += value[1][1]
    total_additional_occ += value[1][2]
    total_missing_occ += value[1][3]

    if head_total_occ + total_missing_occ == 0:
        percent_delta = '0%'
    else:
        percent_delta = f'{round(((total_additional_occ + total_missing_occ) / (head_total_occ + total_missing_occ)) * 100, 2)}%'

    result.insert(0, [repo_name, language, 'Total', 'All', head_total_occ, base_total_occ, percent_delta, total_additional_occ, total_missing_occ])

    if header_flag:
        result.insert(0, ['Repos Name', 'language', 'Collection Id', 'Source Id',
                          f'Total occurrences in {config.HEAD_SHEET_BRANCH_NAME}',
                          f'Total occurrences in {config.BASE_SHEET_BRANCH_NAME}',
                          'Percent Delta',
                          f'Additional Path in {config.HEAD_SHEET_BRANCH_NAME}',
                          f'Missing Path in {config.HEAD_SHEET_BRANCH_NAME}'])

    if write_report:
        write_path_data(f'{os.getcwd()}/output.xlsx', worksheet_name, result)
    return result


def sub_process_occurrences(base_collection_data, head_collection_data, repo_name, language):
    final_result_list = []
    process_collection_base_data = {}
    process_collection_head_data = {}

    head_total_occ = 0
    base_total_occ = 0
    total_additional_occ = 0
    total_missing_occ = 0

    for i in base_collection_data:
        collection_id = i['collectionId']
        source_data = {}
        for j in i['collections']:
            source_id = j['sourceId']
            hash_collections = []
            for occ in j['occurrences']:
                value = json_to_hash(occ)
                hash_collections.append(value)
            source_data[source_id] = hash_collections
        process_collection_base_data[collection_id] = source_data

    for i in head_collection_data:
        collection_id = i['collectionId']
        source_data = {}
        for j in i['collections']:
            source_id = j['sourceId']
            hash_collections = []
            for occ in j['occurrences']:
                value = json_to_hash(occ)
                hash_collections.append(value)
            source_data[source_id] = hash_collections
        process_collection_head_data[collection_id] = source_data

    collection_union = set(process_collection_base_data.keys()).union(set(process_collection_head_data.keys()))

    for collection_id in collection_union:

        if not process_collection_base_data.__contains__(collection_id):
            for source_id in process_collection_head_data[collection_id].keys():
                head_total_occ += len(process_collection_head_data[collection_id][source_id])
                total_additional_occ += len(process_collection_head_data[collection_id][source_id])
                final_result_list.append([repo_name, language, collection_id, source_id, len(process_collection_head_data[collection_id][source_id]), 0, '100%', len(process_collection_head_data[collection_id][source_id]), 0])
            continue

        if not process_collection_head_data.__contains__(collection_id):
            for source_id in process_collection_base_data[collection_id].keys():
                base_total_occ += len(process_collection_base_data[collection_id][source_id])
                total_missing_occ += len(process_collection_base_data[collection_id][source_id])
                final_result_list.append([repo_name, language, collection_id, source_id, 0, len(process_collection_base_data[collection_id][source_id]), '-100%', 0, len(process_collection_base_data[collection_id][source_id])])
            continue

        base_source_data = process_collection_base_data[collection_id]
        head_source_data = process_collection_head_data[collection_id]

        source_union = set(base_source_data.keys()).union(set(head_source_data.keys()))

        for source_id in source_union:

            if not base_source_data.__contains__(source_id):
                total_additional_occ += len(head_source_data[source_id])
                head_total_occ += len(head_source_data[source_id])
                final_result_list.append([repo_name, language, collection_id, source_id, len(head_source_data[source_id]), 0, '100%', len(head_source_data[source_id]), 0])
                continue

            if not head_source_data.__contains__(source_id):
                total_missing_occ += len(base_source_data[source_id])
                base_total_occ += len(base_source_data[source_id])
                final_result_list.append([repo_name, language, collection_id, source_id, 0, len(base_source_data[source_id]), '-100%', 0, len(base_source_data[source_id])])
                continue

            base_occurrence_data = base_source_data[source_id]
            head_occurrence_data = head_source_data[source_id]

            occurrences_union = set(base_occurrence_data).union(set(head_occurrence_data))

            additional_count = 0
            missing_count = 0

            for occ in occurrences_union:

                if not base_occurrence_data.__contains__(occ):
                    additional_count = additional_count + 1

                if not head_occurrence_data.__contains__(occ):
                    missing_count = missing_count + 1

            base_total_occ += len(base_occurrence_data)
            head_total_occ += len(head_occurrence_data)
            total_additional_occ += additional_count
            total_missing_occ += missing_count

            if head_total_occ + total_missing_occ == 0:
                percent_delta = '0%'
            else:
                percent_delta = f'{round(((additional_count + missing_count) / (2 * len(occurrences_union))) * 100, 2)}%'

            final_result_list.append([repo_name, language, collection_id, source_id, len(head_occurrence_data),
                                      len(base_occurrence_data),
                                      percent_delta, additional_count, missing_count])


    return [final_result_list, [head_total_occ, base_total_occ, total_additional_occ, total_missing_occ]]


def process_sources(source_base, source_head, repo_name, language):
    base_sources_count = len(source_base)
    head_sources_count = len(source_head)

    source_set_base = set()
    source_set_head = set()

    for i in source_base: source_set_base.add(i['name'])
    for i in source_head: source_set_head.add(i['name'])

    source_name_head = '\n'.join(source_set_head)
    source_name_base = '\n'.join(source_set_base)

    added = '\n'.join(list(source_set_head.difference(source_set_base)))
    removed = '\n'.join(list(source_set_base.difference(source_set_head)))

    # Nodes present in base, but not in head
    missing_in_head = len(source_set_base.union(source_set_head).difference(source_set_head))
    return [repo_name, language ,'Source','--', head_sources_count, base_sources_count, source_name_head,
            source_name_base, '0 ', added, removed, missing_in_head]


def process_sinks(base_dataflows, head_dataflows, repo_name, scan_status, language ,key='storages'):
    base_sink = base_dataflows[key]
    head_sink = head_dataflows[key]

    sink_set_base = set()
    sink_set_head = set()

    for storage in base_sink:
        for sink in storage['sinks']:
            sink_set_base.add(sink['name'])

    for storage in head_sink:
        for sink in storage['sinks']:
            sink_set_head.add(sink['name'])

    base_sink_count = len(sink_set_base)
    head_sink_count = len(sink_set_head)

    sink_names_base = '\n'.join(sink_set_base)
    sink_names_head = '\n'.join(sink_set_head)

    # percent change in the latest sources wrt stable release
    # try:
    #     percent_change = f'{round((((head_sink_count - base_sink_count) / base_sink_count) * 100), 2)}%'
    # except Exception as e:
    #     percent_change = '0.00%'

    added = '\n'.join(list(sink_set_head.difference(sink_set_base)))
    removed = '\n'.join(list(sink_set_base.difference(sink_set_head)))

    # Nodes present in base, but not in head
    missing_in_head = len(sink_set_base.union(sink_set_head).difference(sink_set_head))
    if scan_status is not None:
        if not scan_status[repo_name].__contains__('missing_sink'):
            scan_status[repo_name]['missing_sink'] = missing_in_head
        else:
            scan_status[repo_name]['missing_sink'] += missing_in_head

    return [repo_name, language ,'Sink', key, head_sink_count, base_sink_count, sink_names_head, sink_names_base, '0',
            added, removed, missing_in_head]


def process_path_analysis(worksheet_name, base_source, head_source, repo_name, language, header_flag, write_report=True):
    result = []

    total_flow_head = 0
    total_flow_base = 0
    total_additional_flow = 0
    total_missing_flow = 0

    for i in ['storages', 'leakages', 'third_parties']:
        value = sub_process_path(base_source['dataFlow'][i], head_source['dataFlow'][i], i, repo_name, language)
        for j in value[0]:
            result.append(j)

        # Add path count in total result
        total_flow_head += value[1][0]
        total_flow_base += value[1][1]
        total_additional_flow += value[1][2]
        total_missing_flow += value[1][3]

    if total_flow_head + total_missing_flow == 0:
        percent_delta = "0%"
    else:
        percent_delta = f"{round((((total_additional_flow + total_missing_flow) / (total_flow_head + total_missing_flow)) * 100), 2)}%"

    result.insert(0, [repo_name, language, 'Total', 'All', 'All', total_flow_head, total_flow_base,
                      total_additional_flow, total_missing_flow, percent_delta])

    if header_flag:
        result.insert(0, ['Repo Name', 'language', 'Sink Category', 'Source', 'Sink', config.HEAD_SHEET_BRANCH_NAME,
                          config.BASE_SHEET_BRANCH_NAME, f'Additional in {config.HEAD_SHEET_BRANCH_NAME}',
                          f'Missing in {config.HEAD_SHEET_BRANCH_NAME}', 'Delta in %',
                          f'Additional Path Id in {config.HEAD_SHEET_BRANCH_NAME}',
                          f'Missing Path ID in {config.HEAD_SHEET_BRANCH_NAME}'])

    # Export to the Excel file
    if write_report:
        write_path_data(f'{os.getcwd()}/output.xlsx', worksheet_name, result)
    return result


def process_unique_path_analysis(worksheet_name, base_source, head_source, repo_name, header_flag, language):
    result = []

    value = sub_process_path(base_source['dataFlow'], head_source['dataFlow'], '---', repo_name, language)

    for j in value[0]:
        result.append(j)

    if header_flag:
        result.insert(0, ['Repo Name', 'language', 'Sink Category', 'Source', 'Sink', config.HEAD_SHEET_BRANCH_NAME,
                          config.BASE_SHEET_BRANCH_NAME, f'Additional in {config.HEAD_SHEET_BRANCH_NAME}',
                          f'Missing in {config.HEAD_SHEET_BRANCH_NAME}', 'Delta in %',
                          f'Additional Path Id in {config.HEAD_SHEET_BRANCH_NAME}',
                          f'Missing Path ID in {config.HEAD_SHEET_BRANCH_NAME}'])

    # Export to the Excel file
    write_path_data(f'{os.getcwd()}/output.xlsx', worksheet_name, result)


def sub_process_path(base_source, head_source, sink_type, repo_name, language):
    final_result_list = []

    # variable used to store the dataflow data
    # Structure :
    #   {sourceId: {sinkId : {path_hash_value : PathId}}}
    process_source_base_data = {}
    process_source_head_data = {}

    total_flow_head = 0
    total_flow_base = 0
    total_additional_flow = 0
    total_missing_flow = 0

    # Process source data and storing all unique hash path value (for base branch)
    for i in base_source:
        source_id = i['sourceId']
        sink_data = {}
        for j in i['sinks']:
            hash_path = {}
            for path in j['paths']:
                temp = [path['path'][0], path['path'][len(path['path']) - 1]]
                value = json_to_hash(temp)
                hash_path[value] = path['pathId']
            sink_data[j['id']] = hash_path
        # Check if sourceID present in dict, If yes then append the sink data in sourceId 
        if process_source_base_data.__contains__(source_id):
            temp_source_data = {**process_source_base_data[source_id], **sink_data}
            process_source_base_data[source_id] = temp_source_data
        else:
            process_source_base_data[source_id] = sink_data

    # Process source data and storing all unique hash path value (for head branch)
    for i in head_source:
        source_id = i['sourceId']
        sink_data = {}
        for j in i['sinks']:
            hash_path = {}
            for path in j['paths']:
                temp = [path['path'][0], path['path'][len(path['path']) - 1]]
                value = json_to_hash(temp)
                hash_path[value] = path['pathId']
            sink_data[j['id']] = hash_path
        # Check if sourceID present in dict, If yes then append the sink data in sourceId 
        if process_source_head_data.__contains__(source_id):
            temp_source_data = {**process_source_head_data[source_id], **sink_data}
            process_source_head_data[source_id] = temp_source_data
        else:
            process_source_head_data[source_id] = sink_data

    source_union = set(process_source_head_data.keys()).union(set(process_source_base_data.keys()))

    # Process source data sequentially for every sourceId present in head and base branch
    for i in source_union:

        # If sourceID is not present in base branch means source Data is addtional w.r.t. head branch
        if not process_source_base_data.__contains__(i):
            for sink in process_source_head_data[i].keys():
                additional_ids = []
                # Add all the ids as additional present inside the head branch because
                # source is not present in base branch
                for id in process_source_head_data[i][sink].keys():
                    additional_ids.append(process_source_head_data[i][sink][id])
                total_flow_head += len(process_source_head_data[i][sink])
                total_additional_flow += len(process_source_head_data[i][sink])
                # Add the flow details in result
                final_result_list.append([repo_name, language ,sink_type, i, sink, len(process_source_head_data[i][sink]), 0,
                                          len(process_source_head_data[i][sink]), 0, '100%', '\n'.join(additional_ids),
                                          0])
            continue

        # If sourceID is not present in head branch means source data is missing w.r.t. head branch
        if not process_source_head_data.__contains__(i):
            for sink in process_source_base_data[i].keys():
                missing_ids = []
                # Add all the ids as missing present inside the base branch because
                # source is not present in head branch
                for id in process_source_base_data[i][sink].keys():
                    missing_ids.append(process_source_base_data[i][sink][id])
                total_flow_base += len(process_source_base_data[i][sink])
                total_missing_flow += len(process_source_base_data[i][sink])
                # Add the flow details in result
                final_result_list.append([repo_name, language ,sink_type, i, sink, 0, len(process_source_base_data[i][sink]), 0,
                                          len(process_source_base_data[i][sink]), '-100%', 0, '\n'.join(missing_ids)])
            continue

        base_sink_data = process_source_base_data[i]
        head_sink_data = process_source_head_data[i]

        sink_union = set(base_sink_data.keys()).union(set(head_sink_data.keys()))

        # Process sink data sequentially for every sinkId present in head and base branch for same sourceId
        for j in sink_union:
            # If sinkId is not present in head branch source means sink data is additional w.r.t. head branch
            if not base_sink_data.__contains__(j):
                additional_ids = []
                # Add all the IDs as additional present inside the head branch sink data
                for id in head_sink_data[j].keys():
                    additional_ids.append(head_sink_data[j][id])
                total_flow_head += len(head_sink_data[j])
                total_additional_flow += len(head_sink_data[j])
                # Add the flow details in result 
                final_result_list.append(
                    [repo_name, language ,sink_type, i, j, len(head_sink_data[j]), 0, len(head_sink_data[j]), 0, '100%',
                     '\n'.join(additional_ids), 0])
                continue

            # If sinkId is not present in base branch source means sink data is missing w.r.t. head branch
            if not head_sink_data.__contains__(j):
                missing_ids = []
                # Add all the IDs as missing present inside the base branch sink data 
                for id in base_sink_data[j].keys():
                    missing_ids.append(base_sink_data[j][id])
                total_flow_base += len(base_sink_data[j])
                total_missing_flow += len(base_sink_data[j])
                # Add the flow details in result
                final_result_list.append(
                    [repo_name, language ,sink_type, i, j, 0, len(base_sink_data[j]), 0, len(base_sink_data[j]), '-100%', 0,
                     '\n'.join(missing_ids)])
                continue

            base_path_data = base_sink_data[j]
            head_path_data = head_sink_data[j]

            missing_path = set()
            new_path = set()

            path_union = set(base_sink_data[j].keys()).union(set(head_sink_data[j].keys()))

            absolute_path_change = 0
            total_path_count = len(path_union)

            # Process path data sequentially for every pathID
            for k in path_union:

                # Add path Id in additional path if not present in base branch sink
                if not base_path_data.__contains__(k):
                    absolute_path_change += 1
                    new_path.add(head_path_data[k])

                # Add path Id in missing path if not present in head branch sink
                elif not head_path_data.__contains__(k):
                    absolute_path_change += 1
                    missing_path.add(base_path_data[k])

            total_flow_head += len(head_path_data)
            total_flow_base += len(base_path_data)
            total_additional_flow += len(new_path)
            total_missing_flow += len(missing_path)
            # Add flow details in result,
            # Here we are calculating the absolute delta w.r.t. total flow found 
            final_result_list.append(
                [repo_name, language ,sink_type, i, j, len(head_path_data), len(base_path_data), len(new_path), len(missing_path),
                 f'{round(((absolute_path_change / (2 * total_path_count)) * 100), 2)}%', '\n'.join(new_path),
                 '\n'.join(missing_path)])

    if total_flow_head + total_missing_flow == 0:
        percent_delta = "0%"
    else:
        percent_delta = f"{round((((total_additional_flow + total_missing_flow) / (total_flow_head + total_missing_flow)) * 100), 2)}%"

    final_result_list.insert(0, [repo_name, language, sink_type, 'All', 'All', total_flow_head, total_flow_base,
                                 total_additional_flow, total_missing_flow, percent_delta])

    return [final_result_list, [total_flow_head, total_flow_base, total_additional_flow, total_missing_flow]]


def json_to_hash(json_obj):
    json_str = json.dumps(json_obj, sort_keys=True)
    hash_object = hashlib.sha256(json_str.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig
