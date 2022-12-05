while true; 
do 
top -b -n1 > ${GITHUB_WORKSPACE}/tools/output.txt;
cat ${GITHUB_WORKSPACE}/tools/output.txt | grep -a '%Cpu(s)' >> ${GITHUB_WORKSPACE}/tools/results_1.txt;
cat ${GITHUB_WORKSPACE}/tools/output.txt | grep -a 'MiB Mem' >> ${GITHUB_WORKSPACE}/tools/results_1.txt;
sleep 60;  # time after which to run the command
done