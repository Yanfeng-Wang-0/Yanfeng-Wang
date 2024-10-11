#!/bin/sh
# Author: yw4524@ic.ac.uk
# Script: tabtocsv.sh
# Description: substitute the tabs in the files with commas
#
# Saves the output into a .csv file
# Arguments: 1 -> tab delimited file
# Date: Oct 2024

#check if input file exist
if [$# -ne 1] ; then
  echo "usage: $0 tab_delimited_file"
  exit 1
fi

#result and cover excessive
echo "Creating a comma delimited version of $1 ..."
tr -s "\t" "," < "$1" > "${1%.txt}.csv"
echo "Done!"
exit