import subprocess


process_1 = subprocess.Popen(["privado", "scan", "~/Privado/repos/java/sample_java", "--overwrite"])
process_2 = subprocess.Popen(["privado", "scan", "~/Privado/repos/java/sample_java", "--overwrite"])


process_1.wait()
process_2.wait()