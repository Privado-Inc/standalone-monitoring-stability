
# Standalone-monitoring-stability


#### Steps to add more repositories in the workflow

1. Create a new branch from `main`
2. Navigate to [repos](https://github.com/Privado-Inc/standalone-monitoring-stability/tree/main/repos) folder
3. Based on the language, open `[language].txt` file
4. Add your repository link at the end. (do not leave any trailing/leading white-spaces or newlines)
5. Raise the PR to `main`
---
If a new file is created in the previous steps, meaning repositories for a new language have been added, follow the below additional steps.

6. Navigate to [Privado Core Comparison Workflow](https://github.com/Privado-Inc/privado-core/blob/d843fa99a0d438c601a51eeaca764874a2313194/.github/workflows/comparison-results.yml#L31)
7. Create a branch from `dev`
8. Add a new element in the array which should be exactly the name of the file added in the previous steps. (without `.txt`)
9. Raise a PR to `dev` and subsequently to `main`
  ```
> NOTE: For ruby, please add a new file `ruby-n` in the comparison workflow and follow steps 1-9. The reason for this is that ruby repos take too much time to scan, and this will hinder the execution time of the workflow.
```

#### Steps to use the standalone-comparison-tool

* Setup

1. Navigate to the directory

2. Run `python3 -m pip install --user virtualenv`

3. Run `python3 -m venv env`

4. Run `source env/bin/activate`

5. Run `pip install -r requirements.txt` to install all the dependencies.

6. Run `python3 ./run.py -f [first_branch] -s [second_branch]`

  
  

* Options

* To specify a custom repository list, use `-r` or `--repos`. Default is `./repos.txt`.

* Run `python3 ./run.py -r path_to_file.txt -f [base_branch] -s [head_branch]`

* To upload the output result to slack, use `--upload`. Default is set to `--no-upload`

* Run `python3 ./run.py -b [base_branch] -h [head_branch] --upload`

* To clear all the previously generated cache and binary data, use `-c`.

* Run `python3 ./run.py -b [base_branch] -h [head_branch] -c`

* To store the privado-core binary for future use, use `-b`

* Run `python3 ./run.py -b [base_branch] -h [head_branch] -b True`. Cache is deleted after each run by default.

* To specify privado branch when comparing privado-core branch, use `-rbb` and `-rbh`

* Run `python3 ./run.py -b [base_branch] -h [head_branch] -rbb [privado_base_branch] -rbh [privado_head_branch]`

* To compare the privado branches, use `-urc`

* Run `python3 ./run.py -rbb [privado_base_branch] -rbh [privado_head_branch] -urc`

* To specify privado-core branch when comparing privado branches, use `-rbb` and `-rbh`

* Run `python3 ./run.py -b [base_branch] -h [head_branch] -rbb [privado_base_branch] -rbh [privado_head_branch] -urc`

* To compare already genereated `privado.json` files, use `-m`

* Run `python3 ./run.py -b [base_privado_json_path] -h [head_privado_json_path] -m`

* To use docker build instead of generating binaries, use `-d` or `--use-docker`

* Run `python3 ./run.py --use-docker -b [base_docker_tag] -h [head_docker_tag]`

  
  

#### Folder structure for storing the results.

```

- temp

- privado

- privado-core

- result

- base_branch

- repo-output.txt --- Contains the scan results

- repo.json --- privado.json for the repository

- head_branch

- repo-output.txt --- Contains the scan results

- repo.json --- privado.json for the repository

```