import csv 
import json
import re
import os
import hashlib

def main(stable_file, dev_file, cpu_usage, stable_time, dev_time):

    try:
        filename = stable_file.split('/')[-1].split('.')[0]
    except:
        print('Please enter a valid file')
        return
    previous_file = open(stable_file)
    current_file = open(dev_file)
    time_data_stable = open(stable_time)
    time_data_dev = open(dev_time)

    # Comes with a newline at the start, so the second element
    try:
        time_final_stable = (time_data_stable.read().split('\n'))
        time_final_dev = (time_data_dev.read().split('\n'))
    except Exception as e:
        print("Error occurced during parsing time data", e)

    for time in time_final_stable:
        if ("elapsed" in time):
            time_value = time.split()[2]
            time_final_stable = time_value.split("e")[0]
            break
    
    for time in time_final_dev:
        if ("elapsed" in time):
            time_value = time.split()[2]
            time_final_dev = time_value.split("e")[0]
            break

    # time_final_dev = time_final_dev.split('\t')[1]
    # time_final_stable = time_final_stable.split('\t')[1]

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

    previous_data = json.load(previous_file)
    current_data = json.load(current_file)

    report = []
    repo_name = previous_data['repoName']

    report.append(['Base Version', '', '', '', 'Head Version'])
    report.append(['privadoCoreVersion', previous_data['privadoCoreVersion'], '', '', 'privadoCoreVersion', current_data['privadoCoreVersion']])
    
    report.append(['privadoCLIVersion', previous_data['privadoCLIVersion'], '', '', 'privadoCLIVersion', current_data['privadoCLIVersion']])

    report.append(['privadoMainVersion', previous_data['privadoMainVersion'], '', '', 'privadoMainVersion', current_data['privadoMainVersion']])
    report.append(["Scan time analytics"])
    report.append(["RepoName", repo_name])
    report.append(['Base version time', '','','', 'Latest version time'])
    report.append([time_final_stable, '','','', time_final_dev])

    report.append([])
    report.append([])
    source_data_stable = previous_data['sources']
    source_data_dev = current_data['sources']
    
    report.append(['Analysis for sources'])
    for row in process_new_sources(source_data_stable, source_data_dev):
        report.append(row)

    report.append([])
    report.append([])

    report.append(['Analysis for collections'])

    for collection in top_level_collection_processor(previous_data['collections'], current_data['collections']):
        for row in collection:
            report.append(row)

    report.append([])
    report.append([])

    dataflow_stable = previous_data['dataFlow']
    dataflow_dev = current_data['dataFlow']

    report.append(['Analysis for Storages Sinks'])

    for row in process_sinks(dataflow_stable, dataflow_dev,key='storages'):
        report.append(row)

    report.append([])
    report.append([])

    report.append(['Analysis for third_parties Sinks'])

    for row in process_sinks(dataflow_stable, dataflow_dev,key='third_parties'):
        report.append(row)

    report.append([])
    report.append([])

    report.append(['Analysis for Leakages Sinks'])

    # for row in process_leakages(dataflow_stable, dataflow_dev, repo_name):
    #     report.append(row)
    for row in process_sinks(dataflow_stable, dataflow_dev,key='leakages'):
        report.append(row)

    report.append([])
    report.append([])
    report.append(["Paths Analysis: Analysis for Leakage DataFlows"])

    for row in process_path_analysis(previous_data, current_data, repo_name):
        report.append(row) 

    report.append([])
    report.append([])

    report.append(["CPU Utilization Report"])
    report.append([""])
    cpu_utilization_data = open(cpu_usage, "r+")

    report.append(["RepoName", repo_name])
    for i in process_cpu_data(cpu_utilization_data.readlines()):
        report.append(i)

    report.append(['--', '--', '--', '--', '--'])
    report.append(['--', '--', '--', '--', '--'])

    create_csv(report)

    previous_file.close()
    current_file.close()

def top_level_collection_processor(collections_stable, collections_dev):
    report = []
    for collection in list(zip(collections_stable, collections_dev)):
        stable_c = collection[0]
        dev_c = collection[1]
        report.append(process_collection(stable_c, dev_c,stable_c['name']))

    return report

def process_collection(collections_stable, collections_dev, collection_name):
    collection_headings = [f'Number of Collections - {collection_name} ( Base ) ', f'Number of Collections - {collection_name} ( Latest )', 'List of  sourceId ( Base )', 'List of  sourceId ( Latest )', '% of change w.r.t base', 'New sourceIds added in Latest', 'Existing sourceIds removed from Latest']
    stable_collections = len(collections_stable['collections'])
    dev_collections = len(collections_dev['collections'])

    collections_sources_stable = []
    collections_sources_dev = []

    for ci in collections_stable['collections']:
        collections_sources_stable.append(ci['sourceId'])

    for ci in collections_dev['collections']:
        collections_sources_dev.append(ci['sourceId'])

    try:
        percent_change = f'{((dev_collections - stable_collections) / stable_collections) * 100}%'  
    except Exception as e:
        print(e)
        percent_change = '0.00%'

    new_latest = '\n'.join(list(set(collections_sources_dev) - set(collections_sources_stable)))
    removed_dev = '\n'.join(list(set(collections_sources_stable) - set(collections_sources_dev)))

    collections_sources_stable = '\n'.join(collections_sources_stable)
    collections_sources_dev = '\n'.join(collections_sources_dev)

    result = [stable_collections, dev_collections, collections_sources_stable, collections_sources_dev, percent_change, new_latest, removed_dev]
    
    return [
        collection_headings,
        list(map(lambda x: x if len(str(x)) else "--", result))
    ]

def process_violations(report, previous_data, current_data):
    
    report.append([])
    report.append([])

    report.append(['Violations Report'])

    report.append([])

    report.append(['Main Version', 'Current Version'])

    previous_count = 0
    current_count = 0

    for i in range(0, min(len(previous_data), len(current_data))):
        report.append([previous_data[previous_count]['policyId'], current_data[current_count]['policyId']])
        previous_count = previous_count + 1
        current_count = current_count + 1

    while previous_count < len(previous_data):
        report.append([previous_data[previous_count]['policyId']])
        previous_count = previous_count + 1

    while current_count < len(current_data):
        report.append(["", current_data[current_count]['policyId']])
        current_count = current_count + 1

def create_csv(data):

    cwd = os.getcwd()
    with open(f'{cwd}/comparison_report.csv', "a") as value:
        report = csv.writer(value)
        for i in data:
            report.writerow(i)

    print("Report written")

def process_new_sources(source_stable, source_dev):

    source_headings = ['Number of Sources ( Base )', 'Number of Sources ( Latest )', 'List of Sources ( Base )', 'List of Sources ( Latest )', '% of change w.r.t base', 'New Sources added in Latest', 'Existing Sources remvoed from Latest']
    stable_sources = len(source_stable)
    dev_sources = len(source_dev)

    source_names_stable = '\n'.join(list(map(lambda x: x['name'], source_stable)))
    source_names_dev = '\n'.join(list(map(lambda x: x['name'], source_dev)))

    # percent change in latest sources wrt stable release
    percent_change = f'{((dev_sources - stable_sources) / stable_sources) * 100}%'   

    new_latest = '\n'.join(list(set(source_names_dev) - set(source_names_stable)))
    removed_dev = '\n'.join(list(set(source_names_stable) - set(source_names_dev)))

    result = [stable_sources, dev_sources, source_names_stable, source_names_dev, percent_change, new_latest, removed_dev]
    
    return [
        source_headings,
        list(map(lambda x: x if len(str(x)) else "--", result))
    ]

def process_sinks(stable_dataflows, dev_dataflows,key='storages'):

    headings = [ 
        f'Number of {key} sinks (base)',
        f'Number of {key} sinks (latest)',
        f'List of {key} Sinks (base)',
        f'List of {key} Sinks ( Latest )',
        '% of change w.r.t base',
        f'New {key} Sinks added in Latest',
        f'Existing {key} Sinks remvoed from Latest'
    ]
    storages_stable = stable_dataflows[key]
    storages_dev = dev_dataflows[key]

    stable_sinks = len(storages_stable) if (len(storages_stable)) else 0
    dev_sinks = len(storages_dev) if (len(storages_dev)) else 0

    sink_names_stable = set()
    sink_names_dev = set()
    for storage in storages_stable:
        for sink in storage['sinks']:
            sink_names_stable.add(sink['name'])
            
    for storage in storages_dev:
        for sink in storage['sinks']:
            sink_names_dev.add(sink['name'])

    sink_names_stable = '\n'.join(sink_names_stable)    
    sink_names_dev = '\n'.join(sink_names_dev)    

    # percent change in latest sources wrt stable release
    try:
        percent_change = f'{round((((dev_sinks - stable_sinks) / stable_sinks) * 100),2)}%'   
    except Exception as e:
        print(e)
        percent_change = '0.00%'
    new_latest = '\n'.join(set(sink_names_dev.split('\n')) - set(sink_names_stable.split('\n')))
    removed_dev = '\n'.join(list(set(sink_names_stable.split('\n')) - set(sink_names_dev.split('\n'))))

    result = [stable_sinks, dev_sinks, sink_names_stable, sink_names_dev, percent_change, new_latest, removed_dev]

    return [headings, list(map(lambda x: x if len(str(x)) else "--", result))]


def process_leakages(stable_dataflows, dev_dataflows, repo_name,key='leakages'):
    headings = [ 
        'repo_name',
        f'Number of {key} sinks (base)',
        f'Number of {key} sinks (latest)',
        f'List of {key} Sinks (base)',
        f'List of {key} Sinks ( Latest )',
        '% of change w.r.t base',
        f'New {key} Sinks added in Latest',
        f'Existing {key} Sinks remvoed from Latest'
    ]

    stable_leakages = stable_dataflows[key]
    dev_leakages = dev_dataflows[key]

    num_stable_leakages = len(stable_leakages)
    num_dev_leakages = len(dev_leakages)

    leakage_names_stable = '\n'.join(list(map(lambda x: x['sourceId'], stable_leakages)))
    leakage_names_dev = '\n'.join(list(map(lambda x: x['sourceId'], dev_leakages)))

    try:
        percent_change = f'{round((((num_dev_leakages - num_stable_leakages) / num_stable_leakages) * 100),2)}%'   
    except Exception as e:
        print(e)
        percent_change = '0.00%'
    new_latest = '\n'.join(set(leakage_names_dev.split('\n')) - set(leakage_names_stable.split('\n'))) 
    removed_dev = '\n'.join(list(set(leakage_names_stable.split('\n')) - set(leakage_names_dev.split('\n'))))
    
    result = [repo_name, num_stable_leakages, num_dev_leakages, leakage_names_stable, leakage_names_dev, percent_change, new_latest, removed_dev]
    
    return [
        headings,
        list(map(lambda x: x if len(str(x)) else "--", result))
    ]

def process_path_analysis(source_stable, source_dev, repo_name):
    path_value = []
    result = []
    delta = []
    result.append(['RepoName', repo_name])
    result.append([])
    path_value.append([])

    for i in range(0, 9):
        delta.append(0)

    for i in ['storages', 'leakages', 'third_parties']:
        value = sub_process_path(source_stable['dataFlow'][i], source_dev['dataFlow'][i], i)
        for j in value[0]:
            path_value.append(j)
        for k in range(0, 9):
            delta[k] += value[1][k]

    result.append(["Total Sources", "Missing Sources", "New Sources"])
    result.append([delta[0], delta[1], delta[2]])
    result.append(["Total Sinks", "Missing Sinks", "New Sinks"])
    result.append([delta[3], delta[4], delta[5]])
    result.append(["Total Paths", "Missing Paths", "New Paths"])
    result.append([delta[6], delta[7], delta[8]])
    for k in path_value:
        result.append(k)

    return result

def sub_process_path(source_stable, source_dev, name):

    final_result_list = []

    process_source_stable_data = {} # Map to store the 
    process_source_dev_data = {}

    path_ids_list = {}

    delta = []
    for i in range(0, 9):
        delta.append(0)

    # Process source data and storing all unique source in set
    for i in source_stable:
        source_id = i['sourceId']
        sink_data = {}
        for j in i['sinks']:
            hash_path = []
            for path in j['paths']:
                temp = [path['path'][0], path['path'][len(path['path']) - 1]]
                value = json_to_hash(temp)
                hash_path.append(value)
                path_ids_list[value] = path['pathId']
            sink_data[j['id']] = hash_path
        process_source_stable_data[source_id] = sink_data

    for i in source_dev:
        source_id = i['sourceId']
        sink_data = {}
        for j in i['sinks']:
            hash_path = []
            for path in j['paths']:
                temp = [path['path'][0], path['path'][len(path['path']) - 1]]
                value = json_to_hash(temp)
                hash_path.append(value)
                path_ids_list[value] = path['pathId']
            sink_data[j['id']] = hash_path
        process_source_dev_data[source_id] = sink_data
    
    source_union = set(process_source_dev_data.keys()).union(set(process_source_stable_data.keys()))
    delta[0] = len(source_union) # total source count

    for i in source_union:

        final_result_list.append([f"{name}: {i}"])

        if not process_source_stable_data.__contains__(i):
            path_count = standalone_source_process(process_source_dev_data[i])
            final_result_list.append(["Total Path in Head", "Total Path in Base (Source Missing)", "%change"])
            final_result_list.append([path_count, "0", "100%"])
            final_result_list.append([])
            delta[2] += 1 # count of new source
            delta[5] += len(list(process_source_dev_data[i].keys()))
            delta[8] += path_count
            continue

        if not process_source_dev_data.__contains__(i):
            path_count = standalone_source_process(process_source_stable_data[i])
            final_result_list.append(["Total Paths in Head (Source Missing)", "Total Paths in Base", "%change"])
            final_result_list.append(["0", path_count, "-100%"])
            final_result_list.append([])
            delta[1] += 1 # count of missing source
            delta[4] += len(list(process_source_stable_data[i].keys()))
            delta[7] += path_count
            continue

        stable_sink_data = process_source_stable_data[i]
        dev_sink_data = process_source_dev_data[i]

        sink_union = set(stable_sink_data.keys()).union(set(dev_sink_data.keys()))
        delta[3] += len(sink_union)

        for j in sink_union:

            final_result_list.append([j])

            if not stable_sink_data.__contains__(j):
                path_count = len(dev_sink_data[j])
                final_result_list.append(["Total Paths in Head", "Total Paths in Base (Sink Missing)", "% Change"])
                final_result_list.append([str(path_count), "0", "100%"])
                delta[5] += 1 # count of new sink
                delta[8] += path_count
                continue
            
            if not dev_sink_data.__contains__(j):
                path_count = len(stable_sink_data[j])
                final_result_list.append(["Total Paths in Head (Sink Missing)", "Total Paths in Base", "% Change"])
                final_result_list.append(["0", str(path_count), "-100%"])
                delta[4] += 1 # count of missing sink
                delta[7] += path_count
                continue

            stable_path_data = stable_sink_data[j]
            dev_path_data = dev_sink_data[j]

            missing_path = set()
            new_path = set()

            path_union = set(stable_path_data).union(set(dev_path_data))
            delta[6] += len(path_union)

            absolute_path_change = 0
            total_path_count = len(path_union)
            temp_result = []

            for k in path_union:

                if not stable_path_data.__contains__(k):
                    absolute_path_change += 1
                    missing_path.add(k)

                elif not dev_path_data.__contains__(k):
                    absolute_path_change += 1
                    new_path.add(k)

            if len(missing_path) != 0:
                temp_result.append(["Missing Path ID in Head"])
                delta[8] += len(missing_path) # count of missing path
                for j in missing_path:
                    temp_result.append([path_ids_list[j]])

            if len(new_path) != 0:
                temp_result.append(["New Path Id in Head"])
                delta[7] += len(new_path) # count of new path
                for j in new_path:
                    temp_result.append([path_ids_list[j]])

            final_result_list.append(["Total Path in Head", "Total Path in Base", "% Change"])
            final_result_list.append([len(stable_path_data), len(dev_path_data), f'{round((( absolute_path_change / (2 * total_path_count)) * 100),2)}%'])

            temp_result.append([])
            for k in temp_result:
                final_result_list.append(k)

    return [final_result_list, delta]

def standalone_source_process(sinks_data):
    
    total_path = 0 
    for i in list(sinks_data.keys()):
        total_path += len(sinks_data[i])
    
    return total_path

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
    main("/utils/privado1.json","/utils/privado.json",0,0,0)