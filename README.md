# Standalone-monitoring-stability

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
		* Run `python3 ./run.py -f [base_branch] -s [head_branch] --upload`
	* To clear all the previously generated cache and binary data, use `-c`. 
		* Run `python3 ./run.py -f [base_branch] -s [head_branch] -c`
	* To store the privado-core binary for future use, use `-b`
		* Run `python3 ./run.py -f [base_branch] -s [head_branch] -b True`. Cache is deleted after each run by default.
	* To compare already genereated `privado.json` files, use `-m`
		* Run `python3 ./run.py -f [base_privado_json_path] -s [head_privado_json_path] -m`
	* To use docker build instead of generating binaries, use `-d` or `--use-docker`
		* Run `python3 ./run.py --use-docker -f [base_docker_tag] -s [head_docker_tag]`


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
