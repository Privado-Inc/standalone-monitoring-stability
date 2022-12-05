import os
import shutil

def delete_temp():
    cwd = os.getcwd()
    path = f'{cwd}/temp/'
    if os.path.isdir(path):
        shutil.rmtree(path)

if __name__ == '__main__':
    delete_temp()