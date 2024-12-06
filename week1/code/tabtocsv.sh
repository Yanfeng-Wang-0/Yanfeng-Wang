# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File name: tabtocsv.sh
# Description: substitute the tabs in the files with commas and saves the output into a .csv file
# Version: 0.0.1
# Date: Oct 2024

# Check if exactly one argument is provided
if [$# -ne 1] ; then
  # Print usage information, showing how to run the script
  echo "usage: $0 tab_delimited_file"
  # Exit with a status code of 1, indicating an error
  exit 1
fi

echo "Creating a comma delimited version of $1 ..."
tr -s "\t" "," < "$1" > "${1%.txt}.csv"
echo "Done!"
exit