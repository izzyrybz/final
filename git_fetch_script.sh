#!/bin/bash


if [ -z "$1" ]; then
  echo "Please provide a repository name as an argument."
  exit 1
fi

cwd=$(pwd)
#echo $cwd
cd "$1"
#echo "moved to the current directory $(pwd)"


# Get the commit history with the desired format
#log=$(git log --graph --pretty=format:'commit:%H,Author:%an,Date:%ad,Parents:%p%nChanged Files:%n' --name-status)

#possible properties
#commit:%H
#Author:%an
#Date:%ad,
#Parents:%p
#Changed files: --name-status)

echo "fetching the git repository information"
log=$(git log --graph --boundary --pretty=format:'%ncommit:%H,Author:%an,Description: %s,Date:%cd,Parents:%p%nChanged Files:%n' --name-status | sed -e 's/^commit/******&/')
#echo $2
#log=$(git log --graph --boundary --pretty=format: '$2' --name-status | sed -e 's/^commit/******&/')

#echo $log

#checking if the file is empty
if [ -s $cwd/logfile.txt ]; then
    #echo "File is not empty, clearing it..."
    > $cwd/logfile.txt
fi

echo "$log" >> $cwd/logfile.txt
