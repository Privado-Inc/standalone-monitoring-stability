import csv 
import json
import re
import os
import hashlib

def main(base_file, head_file, cpu_usage, base_time, head_time, base_branch_name, head_branch_name):

    try:
        filename = base_file.split('/')[-1].split('.')[0]
    except:
        print('Please enter a valid file')
        return
    base_file = open(base_file)
    head_file = open(head_file)
    time_data_base = open(base_time)
    time_data_head = open(head_time)
    
    head_time_value = "NA"
    base_time_value = "NA"

    # Comes with a newline at the start, so the second element
    try:
        time_final_base = (time_data_base.read().split('\n'))
        time_final_head = (time_data_head.read().split('\n'))
    except Exception as e:
        print("Error occurced during parsing time data", e)

    try:
        for time in time_final_base:
            if ("real" in time):
                time_final_base = time
                break
        
        for time in time_final_head:
            if ("real" in time):
                time_final_head = time
                break

        head_time_value = time_final_head.split('\t')[1]
        base_time_value = time_final_base.split('\t')[1]

        # split_minutes_seconds_dev = re.split('[a-zA-Z]+', time_final_dev[:-1]) 
        # split_minutes_seconds_stable = re.split('[a-zA-Z]+', time_final_stable[:-1]) 

        # time_stable_minutes = 0
        # time_dev_minutes = 0
        # minutes_multiplier = 1/60
        
        # for i in range(len(split_minutes_seconds_dev) - 1, -1, -1):
        #     time_dev_minutes += (minutes_multiplier * float(split_minutes_seconds_dev[i]))
        #     minutes_multiplier *= 60
        
        # minutes_multiplier = 1/60
        # for i in range(len(split_minutes_seconds_stable) - 1, -1, -1):
        #     time_stable_minutes += (minutes_multiplier * float(split_minutes_seconds_stable[i]))

        # # Percent change on the latest branch wrt base branch
        # percent_change_time = f'{round(((time_dev_minutes - time_stable_minutes) / time_stable_minutes), 2) * 100}%'

    except Exception as e: 
        for time in time_final_base:
            if ("elapsed" in time):
                time_value = time.split()[2]
                base_time_value = time_value.split("e")[0]
                break
    
        for time in time_final_head:
            if ("elapsed" in time):
                time_value = time.split()[2]
                head_time_value = time_value.split("e")[0]
                break


    base_data = json.load(base_file)
    head_data = json.load(head_file)

    report = []
    repo_name = base_data['repoName']

    report.append(["RepoName", repo_name])
    report.append(["Base Branch Name", base_branch_name])
    report.append(["Head Branch Name", head_branch_name])
    report.append([f'{base_branch_name} Branch run time', base_time_value])
    report.append([f'{head_branch_name} Branch run time', head_time_value])
    report.append([])
    
    report.append(['Analysis for Sources'])
    for row in process_new_sources(base_data['sources'], head_data['sources'], base_branch_name, head_branch_name):
        report.append(row)
    report.append([])

    report.append(['Analysis for Collections'])
    for collection in top_level_collection_processor(base_data['collections'], head_data['collections'], base_branch_name, head_branch_name):
        for row in collection:
            report.append(row)
    report.append([])

    dataflow_base = base_data['dataFlow']
    dataflow_head = head_data['dataFlow']

    report.append(['Analysis for Storages Sinks'])
    for row in process_sinks(dataflow_base, dataflow_head, base_branch_name, head_branch_name, key='storages'):
        report.append(row)
    report.append([])

    report.append(['Analysis for Third Parties Sinks'])
    for row in process_sinks(dataflow_base, dataflow_head, base_branch_name, head_branch_name, key='third_parties'):
        report.append(row)
    report.append([])

    report.append(['Analysis for Leakages Sinks'])
    for row in process_sinks(dataflow_base, dataflow_head, base_branch_name, head_branch_name, key='leakages'):
        report.append(row)
    report.append([])

    report.append(["Paths Analysis: Analysis for Missing and Additional Flows"])
    for row in process_path_analysis(base_data, head_data, repo_name, base_branch_name, head_branch_name):
        report.append(row)

    cpu_utilization_data = open(cpu_usage, "r+")
    report.append(["CPU Utilization Report"])
    for i in process_cpu_data(cpu_utilization_data.readlines()):
        report.append(i)

    report.append([])
    report.append(['---------', '---------', 'END', '---------', '---------'])
    report.append([])
    report.append([])

    create_csv(report)

    base_file.close()
    head_file.close()

# when only need to compare the privado.json file
def compare_files(base_file_uri, head_file_uri):
    if not os.path.isfile(base_file_uri):
        print(f'Please provide complete vaild base file: {base_file_uri}')
        return

    if not os.path.isfile(head_file_uri):
        print(f'Please provide complete vaild head file: {head_file_uri}')
        return

    base_file = open(base_file_uri)
    head_file = open(head_file_uri)
    base_data = json.load(base_file)
    head_data = json.load(head_file)

    report = []

    report.append(["Comparision Result"])
    report.append([])
    report.append(["First File", base_file_uri])
    report.append(["Second File", head_file_uri])
    report.append([])

    report.append(['Analysis for Sources'])
    for row in process_new_sources(base_data['sources'], head_data['sources'], "First", "Second"):
        report.append(row)
    report.append([])

    report.append(['Analysis for Collections'])
    for collection in top_level_collection_processor(base_data['collections'], head_data['collections'], "First", "Second"):
        for row in collection:
            report.append(row)
    report.append([])

    dataflow_base = base_data['dataFlow']
    dataflow_head = head_data['dataFlow']

    report.append(['Analysis for Storages Sinks'])
    for row in process_sinks(dataflow_base, dataflow_head, "First", "Second", key='storages'):
        report.append(row)
    report.append([])

    report.append(['Analysis for Third Parties Sinks'])
    for row in process_sinks(dataflow_base, dataflow_head, "First", "Second", key='third_parties'):
        report.append(row)
    report.append([])

    report.append(['Analysis for Leakages Sinks'])
    for row in process_sinks(dataflow_base, dataflow_head, "First", "Second", key='leakages'):
        report.append(row)
    report.append([])

    report.append(["Paths Analysis: Analysis for Missing and Additional Flows"])
    for row in process_path_analysis(base_data, head_data, "NA", "First", "Second"):
        report.append(row)

    report.append(['---------', '---------', 'END', '---------', '---------'])

    create_csv(report)

    base_file.close()
    head_file.close()


def top_level_collection_processor(collections_base, collections_head, base_branch_name, head_branch_name):
    report = []
    for collection in list(zip(collections_base, collections_head)):
        report.append(process_collection(collection[0], collection[1], collection[0]['name'], base_branch_name, head_branch_name))

    return report

def process_collection(collections_base, collections_head, collection_name, base_branch_name, head_branch_name):
    collection_headings = [f'Number of Collections - {collection_name} ( {base_branch_name} ) ', f'Number of Collections - {collection_name} ( {head_branch_name} )', f'List of  sourceId ( {base_branch_name} )', f'List of  sourceId ( {head_branch_name} )', f'% of change w.r.t {base_branch_name}', f'New sourceIds added in {head_branch_name}', f'Existing sourceIds removed from {head_branch_name}']
    base_collections = len(collections_base['collections'])
    head_collections = len(collections_head['collections'])

    collections_sources_base = []
    collections_sources_head = []

    for ci in collections_base['collections']:
        collections_sources_base.append(ci['sourceId'])

    for ci in collections_head['collections']:
        collections_sources_head.append(ci['sourceId'])

    try:
        percent_change = f'{((head_collections - base_collections) / head_collections) * 100}%'  
    except Exception as e:
        percent_change = '0.00%'

    latest = '\n'.join(list(set(collections_sources_head).difference(set(collections_sources_base))))
    removed = '\n'.join(list(set(collections_sources_base).difference(set(collections_sources_head))))

    collections_sources_base = '\n'.join(collections_sources_base)
    collections_sources_head = '\n'.join(collections_sources_head)

    result = [base_collections, head_collections, collections_sources_base, collections_sources_head, percent_change, latest, removed]
    
    return [
        collection_headings,
        list(map(lambda x: x if len(str(x)) else "--", result))
    ]

# def process_violations(report, previous_data, current_data):
    
#     report.append([])
#     report.append([])

#     report.append(['Violations Report'])

#     report.append([])

#     report.append(['Main Version', 'Current Version'])

#     previous_count = 0
#     current_count = 0

#     for i in range(0, min(len(previous_data), len(current_data))):
#         report.append([previous_data[previous_count]['policyId'], current_data[current_count]['policyId']])
#         previous_count = previous_count + 1
#         current_count = current_count + 1

#     while previous_count < len(previous_data):
#         report.append([previous_data[previous_count]['policyId']])
#         previous_count = previous_count + 1

#     while current_count < len(current_data):
#         report.append(["", current_data[current_count]['policyId']])
#         current_count = current_count + 1

def create_csv(data):

    cwd = os.getcwd()
    with open(f'{cwd}/comparison_report.csv', "a") as value:
        report = csv.writer(value)
        for i in data:
            report.writerow(i)

    print(f'Report written and exported to: {cwd}/comparison_report.csv')

def process_new_sources(source_base, source_head, base_branch_name, head_branch_name):

    source_headings = [f'Number of Sources ( {base_branch_name} )', f'Number of Sources ( {head_branch_name} )', f'List of Sources ( {base_branch_name} )', f'List of Sources ( {head_branch_name} )', '% change', f'New Sources added in {head_branch_name}', f'Missing Sources in {head_branch_name}']
    base_sources = len(source_base)
    head_sources = len(source_head)

    source_names_base = '\n'.join(list(map(lambda x: x['name'], source_base)))
    source_names_head = '\n'.join(list(map(lambda x: x['name'], source_head)))

    # percent change in latest sources wrt stable release
    try:
        percent_change = f'{((head_sources - base_sources) / base_sources) * 100}%'
    except:
        percent_change = '0.00%'

    latest = '\n'.join(list(set(source_names_head).difference(set(source_names_base))))
    removed = '\n'.join(list(set(source_names_base).difference(set(source_names_head))))

    result = [base_sources, head_sources, source_names_base, source_names_head, percent_change, latest, removed]
    
    return [
        source_headings,
        list(map(lambda x: x if len(str(x)) else "--", result))
    ]

def process_sinks(base_dataflows, head_dataflows, base_branch_name, head_branch_name, key='storages'):

    headings = [ 
        f'Number of {key} sinks ( {base_branch_name} )',
        f'Number of {key} sinks ( {head_branch_name} )',
        f'List of {key} Sinks ( {base_branch_name})',
        f'List of {key} Sinks ( {head_branch_name} )',
        f'% of change w.r.t. {head_branch_name}',
        f'New {key} Sinks added in {head_branch_name}',
        f'Existing {key} Sinks remvoed from {head_branch_name}'
    ]
    base_sink = base_dataflows[key]
    head_sink = head_dataflows[key]

    base_sink_count = len(base_sink)
    head_sink_count = len(head_sink)

    sink_set_base = set()
    sink_set_head = set()

    for storage in base_sink:
        for sink in storage['sinks']:
            sink_set_base.add(sink['name'])
            
    for storage in head_sink:
        for sink in storage['sinks']:
            sink_set_head.add(sink['name'])

    sink_names_base = '\n'.join(sink_set_base)    
    sink_names_head = '\n'.join(sink_set_head)

    # percent change in latest sources wrt stable release
    try:
        percent_change = f'{round((((head_sink_count - base_sink_count) / base_sink_count) * 100),2)}%'   
    except Exception as e:
        percent_change = '0.00%'
    
    latest = '\n'.join(list(sink_set_head.difference(sink_set_base)))
    removed = '\n'.join(list(sink_set_base.difference(sink_set_head)))

    result = [base_sink_count, head_sink_count, sink_names_base, sink_names_head, percent_change, latest, removed]

    return [headings, list(map(lambda x: x if len(str(x)) else "--", result))]

def process_path_analysis(base_source, head_source, repo_name, base_branch_name, head_branch_name):
    path_value = []
    result = []
    delta = []
    result.append(['RepoName', repo_name])
    result.append([])
    path_value.append([])

    for i in range(0, 9):
        delta.append(0)

    for i in ['storages', 'leakages', 'third_parties']:
        value = sub_process_path(base_source['dataFlow'][i], head_source['dataFlow'][i], i, base_branch_name, head_branch_name)
        for j in value[0]:
            path_value.append(j)
        for k in range(0, 8):
            delta[k] += value[1][k]
        path_value.append([])

    result.append([f'Total Sources in {head_branch_name}', f'Total Sources in {base_branch_name}', "Additional Sources", "Missing Sources", "Delta %"])
    result.append([delta[0], delta[1], delta[2], delta[3], 0])
    result.append([f'Total Sinks in {head_branch_name}', f'Total Sinks in {base_branch_name}', "Additinal Sinks", "Missing Sinks", "Delta %"])
    result.append([delta[4], delta[5], delta[6], delta[7], 0])

    for k in path_value:
        result.append(k)

    return result

def sub_process_path(base_source, head_source, name, base_branch_name, head_branch_name):
    
    final_result_list = []

    process_source_base_data = {}
    process_source_head_data = {}

    total_flow_head = 0
    total_flow_base = 0

    delta = []
    for i in range(0, 8):
        delta.append(0)

    # Process source data and storing all unique source in set
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
        if process_source_base_data.__contains__(source_id):
            process_source_base_data[source_id][j['id']] = hash_path
        else:
            process_source_base_data[source_id] = sink_data

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
        if process_source_head_data.__contains__(source_id):
            process_source_head_data[source_id][j['id']] = hash_path
        else:
            process_source_head_data[source_id] = sink_data
    
    source_union = set(process_source_head_data.keys()).union(set(process_source_base_data.keys()))
    delta[0] = len(process_source_head_data.keys()) # total source count in Head
    delta[1] = len(process_source_base_data.keys())

    final_result_list.append([f'Flow ({name})', head_branch_name, base_branch_name, f'Additional in {head_branch_name}', f'Missing in {head_branch_name}', "Delta in %", "Additional Path ID", "Missing Path Id"])

    for i in source_union:

        if not process_source_base_data.__contains__(i):
            delta[2] += 1 
            delta[6] += len(list(process_source_head_data[i].keys()))
            delta[4] += len(list(process_source_head_data[i].keys()))
            for sink in process_source_head_data[i].keys():
                additional_ids = []
                for id in process_source_head_data[i][sink].keys():
                    additional_ids.append(process_source_head_data[i][sink][id])
                total_flow_head += len(process_source_head_data[i][sink])
                final_result_list.append([f'{name}: {i} -> {sink}', len(process_source_head_data[i][sink].keys()), 0, len(process_source_head_data[i][sink].keys()), 0, "100%", '\n'.join(additional_ids), 0])
            continue

        if not process_source_head_data.__contains__(i):
            delta[3] += 1 
            delta[7] += len(list(process_source_base_data[i].keys()))
            delta[5] += len(list(process_source_base_data[i].keys()))
            for sink in process_source_base_data[i].keys():
                missing_ids = []
                for id in process_source_base_data[i][sink].keys():
                    missing_ids.append(process_source_base_data[i][sink][id])
                total_flow_base += len(process_source_base_data[i][sink])
                final_result_list.append([f'{name}: {i} -> {sink}', 0, len(process_source_base_data[i][sink].keys()), 0, len(process_source_base_data[i][sink].keys()), "-100%", 0,'\n'.join(missing_ids)])
            continue

        base_sink_data = process_source_base_data[i]
        head_sink_data = process_source_head_data[i]

        sink_union = set(base_sink_data.keys()).union(set(head_sink_data.keys()))
        delta[4] += len(head_sink_data.keys())
        delta[5] += len(base_sink_data.keys())

        for j in sink_union:
            if not base_sink_data.__contains__(j):
                delta[6] += 1 
                additional_ids = []
                for id in head_sink_data[j].keys():
                    additional_ids.append(head_sink_data[j][id])
                total_flow_head += len(head_sink_data[j])
                final_result_list.append([f'{name}: {i} -> {j}', len(head_sink_data[j].keys()), 0, len(head_sink_data[j].keys()), 0, "100%", '\n'.join(additional_ids),0])
                continue
            
            if not head_sink_data.__contains__(j):
                delta[7] += 1 
                missing_ids = []
                for id in base_sink_data[j].keys():
                    missing_ids.append(base_sink_data[j][id])
                total_flow_base += len(base_sink_data[j])
                final_result_list.append([f'{name}: {i} -> {j}', 0, len(base_sink_data[j].keys()), 0, len(base_sink_data[j].keys()), "-100%", 0 ,'\n'.join(missing_ids)])
                continue

            base_path_data = base_sink_data[j]
            head_path_data = head_sink_data[j]

            missing_path = set()
            new_path = set()

            path_union = set(base_sink_data[j].keys()).union(set(head_sink_data[j].keys()))

            absolute_path_change = 0
            total_path_count = len(path_union)

            for k in path_union:

                if not base_path_data.__contains__(k):
                    absolute_path_change += 1
                    new_path.add(head_path_data[k])

                elif not head_path_data.__contains__(k):
                    absolute_path_change += 1
                    missing_path.add(base_path_data[k])

            total_flow_head += len(head_path_data)
            total_flow_base += len(base_path_data)
            final_result_list.append([f'{name}: {i} -> {j}', len(head_path_data), len(base_path_data), len(new_path), len(missing_path), f'{round((( absolute_path_change / (2 * total_path_count)) * 100),2)}%', '\n'.join(new_path), '\n'.join(missing_path)])

    final_result_list.insert(1, ['Total Flows', total_flow_head, total_flow_base])
    return [final_result_list, delta]

def json_to_hash(json_obj):
    json_str = json.dumps(json_obj, sort_keys=True)
    hash_object = hashlib.sha256(json_str.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig

def process_cpu_data(cpu_utilization_data):

    final_result_list = []

    for i in range(0, len(cpu_utilization_data)):
        cpu_data = cpu_utilization_data[i].split(',')
        value = []
        for j in range(0, len(cpu_data)):
            if j == 0:
                v = cpu_data[j].split(':')
                value.append(v[0])
                value.append(v[1])
            else:
                value.append(cpu_data[j])
        final_result_list.append(value)

        if i%2 == 1:
            final_result_list.append([])

    return final_result_list

if __name__ == "__main__":
    main("/utils/privado.json","/utils/privado1.json",0,0,0, "ankit", "kk")