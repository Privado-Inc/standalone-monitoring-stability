import csv 
import sys
import json
import re
import os

def main(stable_file, dev_file, cpu_usage, stable_time, dev_time):

    try:
        filename = stable_file.split('/')[-1].split('.')[0]
    except:
        print('Please enter a valid file')
        return
    print(filename)
    previous_file = open(stable_file)
    current_file = open(dev_file)
    time_data_stable = open(stable_time)
    time_data_dev = open(dev_time)

    # Comes with a newline at the start, so the second element
    time_final_stable =  (time_data_stable.read().split('\n')[1]).split('\t')[1]
    time_final_dev =  (time_data_dev.read().split('\n')[1]).split('\t')[1]



    split_minutes_seconds_dev = re.split('[a-zA-Z]+', time_final_dev[:-1]) 
    split_minutes_seconds_stable = re.split('[a-zA-Z]+', time_final_stable[:-1]) 

    time_stable_minutes = 0
    time_dev_minutes = 0
    minutes_multiplier = 1/60
    


    for i in range(len(split_minutes_seconds_dev) - 1, -1, -1):
        time_dev_minutes += (minutes_multiplier * float(split_minutes_seconds_dev[i]))
        minutes_multiplier *= 60
    
    minutes_multiplier = 1/60
    for i in range(len(split_minutes_seconds_stable) - 1, -1, -1):
        time_stable_minutes += (minutes_multiplier * float(split_minutes_seconds_stable[i]))


    # Percent change on the latest branch wrt base branch
    percent_change_time = f'{round(((time_dev_minutes - time_stable_minutes) / time_stable_minutes), 2) * 100}%'


    previous_data = json.load(previous_file)
    current_data = json.load(current_file)

    report = []
    repo_name = previous_data['repoName']






    report.append(['Base Version', '', '', '', 'Latest Version'])
    report.append(['privadoCoreVersion', previous_data['privadoCoreVersion'], '', '', 'privadoCoreVersion', current_data['privadoCoreVersion']])
    
    report.append(['privadoCLIVersion', previous_data['privadoCLIVersion'], '', '', 'privadoCLIVersion', current_data['privadoCLIVersion']])

    report.append(['privadoMainVersion', previous_data['privadoMainVersion'], '', '', 'privadoMainVersion', current_data['privadoMainVersion']])
    report.append(["Scan time analytics"])
    report.append(["RepoName", repo_name])
    report.append(['Base version time', '','','', 'Latest version time', '', '% change wrt base'])
    report.append([time_final_stable, '','','', time_final_dev, '', percent_change_time])


    report.append([])
    report.append([])
    source_data_stable = previous_data['sources']
    source_data_dev = current_data['sources']
    
    report.append(['Analysis for sources'])
    for row in process_new_sources(source_data_stable, source_data_dev, repo_name):
        report.append(row)

    report.append([])
    report.append([])

    dataflow_stable = previous_data['dataFlow']
    dataflow_dev = current_data['dataFlow']

    report.append(['Analysis for Storages Sinks'])

    for row in process_sinks(dataflow_stable, dataflow_dev, repo_name,key='storages'):
        report.append(row)

    report.append([])
    report.append([])


    report.append(['Analysis for third_parties Sinks'])

    for row in process_sinks(dataflow_stable, dataflow_dev, repo_name,key='third_parties'):
        report.append(row)

    
    report.append([])
    report.append([])


    report.append(['Analysis for collections'])

    for collection in top_level_collection_processor(previous_data['collections'], current_data['collections'], repo_name):
        for row in collection:
            report.append(row)

    report.append([])
    report.append([])

    report.append(['Analysis for Leakages DataFlows'])

    for row in process_leakages(dataflow_stable, dataflow_dev, repo_name):
        report.append(row)

    report.append([])
    report.append([])
    report.append(["NUMBER OF PATHS ANANLYSIS: Analysis for Leakage DataFlows"])

    for row in process_path_analysis(previous_data, current_data, repo_name):
        report.append(row) 

    report.append([])
    report.append([])
    



    

    
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


def top_level_collection_processor(collections_stable, collections_dev, repo_name):
    report = []
    for collection in list(zip(collections_stable, collections_dev)):
        stable_c = collection[0]
        dev_c = collection[1]
        report.append(process_collection(stable_c, dev_c, repo_name,stable_c['name']))

    return report


def process_collection(collections_stable, collections_dev, repo_name, collection_name):
    collection_headings = ['repo_name', f'Number of Collections - {collection_name} ( Base ) ', f'Number of Collections - {collection_name} ( Latest )', 'List of  sourceId ( Base )', 'List of  sourceId ( Latest )', '% of change w.r.t base', 'New sourceIds added in Latest', 'Existing sourceIds removed from Latest']
    print(collections_stable['collections'])
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
    except:
        percent_change = '0.00%'


    new_latest = '\n'.join(list(set(collections_sources_dev) - set(collections_sources_stable)))
    removed_dev = '\n'.join(list(set(collections_sources_stable) - set(collections_sources_dev)))

    collections_sources_stable = '\n'.join(collections_sources_stable)
    collections_sources_dev = '\n'.join(collections_sources_dev)

    result = [repo_name, stable_collections, dev_collections, collections_sources_stable, collections_sources_dev, percent_change, new_latest, removed_dev]
    
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



def process_new_sources(source_stable, source_dev, repo_name):

    source_headings = ['repo_name', 'Number of Sources ( Base )', 'Number of Sources ( Latest )', 'List of Sources ( Base )', 'List of Sources ( Latest )', '% of change w.r.t base', 'New Sources added in Latest', 'Existing Sources remvoed from Latest']
    stable_sources = len(source_stable)
    dev_sources = len(source_dev)

    source_names_stable = '\n'.join(list(map(lambda x: x['name'], source_stable)))
    source_names_dev = '\n'.join(list(map(lambda x: x['name'], source_dev)))

    # percent change in latest sources wrt stable release
    percent_change = f'{((dev_sources - stable_sources) / stable_sources) * 100}%'   

    new_latest = '\n'.join(list(set(source_names_dev) - set(source_names_stable)))
    removed_dev = '\n'.join(list(set(source_names_stable) - set(source_names_dev)))

    result = [repo_name, stable_sources, dev_sources, source_names_stable, source_names_dev, percent_change, new_latest, removed_dev]
    
    return [
        source_headings,
        list(map(lambda x: x if len(str(x)) else "--", result))
    ]



def process_sinks(stable_dataflows, dev_dataflows, repo_name,key='storages'):

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
    except:
        percent_change = '0.00%'
    new_latest = '\n'.join(set(sink_names_dev.split('\n')) - set(sink_names_stable.split('\n')))
    removed_dev = '\n'.join(list(set(sink_names_stable.split('\n')) - set(sink_names_dev.split('\n'))))

    result = [repo_name, stable_sinks, dev_sinks, sink_names_stable, sink_names_dev, percent_change, new_latest, removed_dev]

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
    except:
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
    path_value.append(['RepoName', repo_name])
    path_value.append([])

    for i in ['storages', 'leakages', 'third_parties']:
        for i in sub_process_path(source_stable['dataFlow'][i], source_dev['dataFlow'][i], i):
            path_value.append(i)

    return path_value


def sub_process_path(source_stable, source_dev, value):

    final_result_list = []

    process_stable_data = {}
    process_dev_data = {}
    
    source_data_list = set()

    for i in source_stable:
        source_id = i['sourceId']
        sinks_data = {}
        for j in i['sinks']:
            sinks_data[j['id']] = len(j['paths'])
        process_stable_data[source_id] = sinks_data
        source_data_list.add(i['sourceId'])

    for i in source_dev:
        source_id = i['sourceId']
        sinks_data = {}
        for j in i['sinks']:
            sinks_data[j['id']] = len(j['paths'])
        process_dev_data[source_id] = sinks_data
        source_data_list.add(i['sourceId'])

    for i in source_data_list:

        sub_heading_list = []
        sub_title_list = []
        sub_result_list = []
        counter = 1

        base_list = process_stable_data[i] if process_stable_data.__contains__(i) else []
        dev_list = process_dev_data[i] if process_dev_data.__contains__(i) else []
        sinks_list = set()

        for j in base_list:
            sinks_list.add(j)

        for j in dev_list:
            sinks_list.add(j)

        for j in sinks_list:
            base_count = base_list[j] if j in base_list else "NA"
            dev_count = dev_list[j] if j in dev_list else "NA"

            path_flow = str(counter) + " : " + str(i) + " -> " + str(j)
            complete_path = "DataFlow -> " + value + " -> " + str(i) + " -> " + str(j)

            sub_heading_list.append('\n'.join([path_flow, complete_path]))
            sub_heading_list.append("")
            sub_heading_list.append("")
            sub_title_list.append("Base")
            sub_title_list.append("Latest")
            sub_title_list.append("% Change")
            sub_result_list.append(base_count)
            sub_result_list.append(dev_count)
            try:
                sub_result_list.append(f'{((dev_count - base_count) / base_count) * 100}%')
            except:
                sub_result_list.append('0.00%')
            counter = counter + 1

        final_result_list.append(sub_heading_list)
        final_result_list.append(sub_title_list)
        final_result_list.append(sub_result_list)
        final_result_list.append([])
    
    return final_result_list

def process_cpu_data(cpu_utilization_data):

    final_result_list = []

    for i in range(0, len(cpu_utilization_data)):
        cpu_data = cpu_utilization_data[i].split(',')
        value = []
        for j in range(0, len(cpu_data)):
            if j == 0:
                v = cpu_data[j].split(':')
                print(v[0])
                print(v[1])
                value.append(v[0])
                value.append(v[1])
            else:
                value.append(cpu_data[j])
        final_result_list.append(value)

        if i%2 == 1:
            final_result_list.append([])

    return final_result_list

if __name__ == "__main__":
    main()