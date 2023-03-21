import subprocess
import os

from process_logfile import process_logfile




print("#"*80)
print("Welcome to the kms process")
print("#"*80)

repo = input("Please provide the path that the repo is saved under, from the file you are in right now \n(Example: ../rdf_code) \n")
repo = '../rdf_code'
process = subprocess.Popen(['./git_fetch_script.sh', repo], stdout=subprocess.PIPE)
output, error = process.communicate()
print(output.decode())

if (os.path.dirname(os.path.realpath('logfile.txt'))):

    ttl_file_path = process_logfile('logfile.txt')

