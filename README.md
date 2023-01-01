# Standalone-monitoring-stability

Steps to use the standalone-comparison-tool
* Setup
	1. Navigate to the directory
	2. Run `python3 -m pip install --user virtualenv`
	3. Run `python3 -m venv env`
	4. Run `source env/bin/activate`
	5. Run `pip install -r requirements.txt` to install all the dependencies.
	6. Run `python3 ./run.py -f [first_branch] -s [second_branch]`

* To use the previous privado file download
    *   Run `python3 ./run.py -f [first_branch] -s [second_branch] -c`

* To specify a custom repository list:
	*  Create a file `your-repos.txt` which should be a new-line separated list of *public* repository links hosted on Github. 
	*  Run `python3 ./run.py -r path_to_file.txt`
 
 * To skip sending results to slack: 
	 * Run `python3 ./run.py -r path_to_file.txt --no-upload`
