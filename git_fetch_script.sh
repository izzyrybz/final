#!/bin/bash


if [ -z "$1" ]; then
  echo "Please provide a repository name as an argument."
  exit 1
fi

cwd=$(pwd)
echo $cwd
cd "$1"
echo "moved to the current directory $(pwd)"


# Get the commit history with the desired format
#log=$(git log --graph --pretty=format:'commit:%H,Author:%an,Date:%ad,Parents:%p%nChanged Files:%n' --name-status)
log=$(git log --graph --boundary --pretty=format:'commit:%H,Author:%an,Date:%ad,Parents:%p%nChanged Files:%n' --name-status | sed -e 's/^commit/******&/')
#echo $log

echo "$log" >> $cwd/logfile.txt
