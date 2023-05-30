import os

def build():
    path = f'{os.get_cwd()}/temp/privado-core'
    os.system(f"cd {path} && sbt clean stage | tee {os.getcwd()}/temp/build_output.txt")

build()
