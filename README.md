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
