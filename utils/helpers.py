import builder
from utils.DiffCache import update_count, update_count_time_diffcache


def print_timestamp(message):
    print(f"{builder.get_current_time()} - {message}")

def add_to_diff_cache(diff_cache_key, additional, missing):
    if additional > 0:
        update_count(diff_cache_key, "additional")
    if missing > 0:
        update_count(diff_cache_key, "missing")

    if additional == 0 and missing == 0:
        update_count(diff_cache_key, "matching")

def add_to_time_diff_cache(diff_cache_key, diff):
    if diff >= 0:
        update_count_time_diffcache(diff_cache_key, "more", abs(diff))
    else:
        update_count_time_diffcache(diff_cache_key, "less", abs(diff))

def get_missing_additional_from_row(row: list):
    try:
        return row[-1], row[-3].count("\n")
    except IndexError as iex:
        print_timestamp("[Error]: The row supplied does not comply with the standard size.")
        print(iex)

