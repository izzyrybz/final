import subprocess
import os

from process_logfile import process_logfile

'''import sys
sys.path.append('/home/bell/rdf_code/ownbuild.py')
import ownbuild'''

print("#"*80)
print("Welcome to the kms process")
print("#"*80)

#possible option in the future to let user enter the attributes that they want to look at and then extend the process_logfile
#attri = input("Please provide the attributes investigate, such as commit hash, user, date, ect \n(read more on : https://git-scm.com/docs/git-log) \n")
#attri = '%ncommit:%H,Author:%an,Description: %s,Date:%cd,Parents:%p%nChanged Files:%n'
#process = subprocess.Popen(['./git_fetch_script.sh', repo, attri], stdout=subprocess.PIPE)

repo = input("Please provide the path that the repo is saved under, from the file you are in right now \n(Example: ../rdf_code) \n")

repo = '../rdf_code'

process = subprocess.Popen(['./git_fetch_script.sh', repo], stdout=subprocess.PIPE)

output, error = process.communicate()
print(output.decode())

if (os.path.dirname(os.path.realpath('logfile.txt'))):

    ttl_file_path = process_logfile('logfile.txt')

#ownbuild.main(question)

