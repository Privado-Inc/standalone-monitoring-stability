while true; 
do 
top -b -n1 > $(pwd)/temp/output.txt;
cat $(pwd)/temp/output.txt | grep -a '%Cpu(s)' >> $(pwd)/temp/result/$2/$1_cpu_mem.txt; # $1 is the repo name, and $2 is the mode, dev or stable
cat $(pwd)/temp/output.txt | grep -a 'MiB Mem' >> $(pwd)/temp/result/$2/$1_cpu_mem.txt;
sleep 60;  # time after which to run the command
done