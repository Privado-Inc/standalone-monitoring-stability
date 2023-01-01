import os
import shutil

def delete_action(action):

    if action:
        hard_clean()
    else:
        soft_clean()

# delete all temp file expect privado-core and privado
def soft_clean():
    delete_dir("/temp/binary/")
    delete_dir("/temp/cpu_mem/")
    delete_dir("/temp/repos")
    delete_dir("/result/")

# delete all temp file
def hard_clean():
    delete_dir("/temp/")

def delete_dir(path):
    cwd = os.getcwd()
    delete_path = f'{cwd}{path}'
    if os.path.isdir(delete_path):
        shutil.rmtree(delete_path, ignore_errors=False)

def clean_after_scan():
    delete_dir("/temp/binary/")
    delete_dir("/temp/repos/")