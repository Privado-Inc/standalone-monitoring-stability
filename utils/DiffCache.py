
blueprint_keys = ["matching","missing", "additional"]
ValueBlueprint = {k: 0 for k in blueprint_keys}

keys = ["sources", "sinks", "dataflows", "collections"]
DiffCache = {k: ValueBlueprint.copy() for k in keys}

def update_count(key, blueprint_key, increment_by=1):
    if key not in keys:
        print("Invalid key")
        return

    if blueprint_key not in blueprint_keys:
        print("Invalid blueprint key: Should be matching, missing, or additional.")
        return

    DiffCache[key][blueprint_key] += increment_by