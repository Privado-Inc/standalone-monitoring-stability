import os
import shutil

def delete_temp():
    cwd = os.getcwd()
    path = f'{cwd}/temp/'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False)

delete_temp()