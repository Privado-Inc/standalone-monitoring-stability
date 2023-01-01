while true; 
do 
top -l 1 > $(pwd)/temp/cpu_mem/output.txt;
cat $(pwd)/temp/cpu_mem/output.txt | grep -a 'CPU usage' >> $(pwd)/temp/cpu_mem/$1_cpu_mem.txt; # $1 is the repo name, and $2 is the mode, dev or stable
cat $(pwd)/temp/cpu_mem/output.txt | grep -a 'MemRegions' >> $(pwd)/temp/cpu_mem/$1_cpu_mem.txt;
sleep 60;  # time after which to run the command
done