
blueprint_keys = ["matching","missing", "additional"]
time_blueprint_keys = ["more", "less"]

ValueBlueprint = {k: 0 for k in blueprint_keys}
TimeValueBluePrint = {k: [0, 0] for k in time_blueprint_keys}

keys = ["reachable_by_flow_count", "sources", "sinks", "dataflows", "collections"]
time_keys = ["scan_time", "reachable_by_flow_time"]

DiffCache = {k: ValueBlueprint.copy() for k in keys}
TimeDiffCache = {k: TimeValueBluePrint.copy() for k in time_keys }


def update_count(key, blueprint_key, increment_by=1):
    if key not in keys:
        print("Invalid key")
        return

    if blueprint_key not in blueprint_keys:
        print("Invalid blueprint key: Should be matching, missing, or additional.")
        return

    DiffCache[key][blueprint_key] += increment_by
    print(DiffCache)

def update_count_time_diffcache(key, blueprint_key, value, increment_by=1):
    if key not in time_keys:
        print("Invalid key")
        return

    if blueprint_key not in time_blueprint_keys:
        print("Invalid blueprint key: Should be more or less.")
        return

    TimeDiffCache[key][blueprint_key] = [TimeDiffCache[key][blueprint_key][0] + increment_by, TimeDiffCache[key][blueprint_key][1] + value]
    print(TimeDiffCache)