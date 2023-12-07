import subprocess


process_1 = subprocess.Popen(['export', '_JAVA_OPTIONS=-Xmx14G', '&&', 'cd', '/home/ubuntu/standalone-monitoring-stability/temp/binary/Privado-Inc-main@Privado-Inc-main/bin', '&&', './privado-core', 'scan', '/home/ubuntu/standalone-monitoring-stability/temp/repos/Library-Assistant', '-ic', '/home/ubuntu/standalone-monitoring-stability/temp/privado/Privado-Inc-main@Privado-Inc-main', '--skip-upload', '--test-output', '2>&1', '|', 'tee', '-a', '/home/ubuntu/standalone-monitoring-stability/temp/result/Privado-Inc-main@Privado-Inc-main/Library-Assistant-output.txt'])
process_2 = subprocess.Popen(["privado", "scan", "~/Privado/repos/java/sample_java", "--overwrite"])


process_1.wait()
process_2.wait()