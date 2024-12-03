# This file is intended to process the stageMetadata.json file generated by privado-core-enterprise
import json

from utils.helpers import add_to_time_diff_cache, add_to_diff_cache


def get_summary_extract(file_path):
    with open(file_path) as f:
        metadata_object = json.loads(f.read())

        stage_metadata_time = "stageTime"
        stage_metadata_count = "stageCount"

        time_keys = ["Finding flows", "Total time"]
        count_keys = ["Unique flows"]

        result = dict({k: metadata_object[stage_metadata_time].get(k, 0) for k in time_keys})
        result.update({j: metadata_object[stage_metadata_count].get(j, 0) for j in count_keys})

        return result


def update_diff_cache(base_summary_extract, head_summary_extract):
    finding_flows_key = "Finding flows"
    total_time_key = "Total time"
    unique_flows_key = "Unique flows"

    flow_time_diff = head_summary_extract[finding_flows_key] - base_summary_extract[finding_flows_key]
    total_time_diff = head_summary_extract[total_time_key] - base_summary_extract[total_time_key]
    unique_flows_diff = head_summary_extract[unique_flows_key] - base_summary_extract[unique_flows_key]

    add_to_time_diff_cache("reachable_by_flow_time", flow_time_diff)
    add_to_time_diff_cache("scan_time", total_time_diff)

    if unique_flows_diff > 0:
        add_to_diff_cache("reachable_by_flow_count", unique_flows_diff, 0)
    else:
        add_to_diff_cache("reachable_by_flow_count", 0, unique_flows_diff)
