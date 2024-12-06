# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: ConcatenateTwoFiles.sh
# Description: merge two .csv into one 
# Version: 0.0.1
# Date: Oct 2024

# Check if the number of arguments is exactly 3
if [$# -ne 3] ; then
# Print usage instructions if incorrect number of arguments is provided
  echo "usage : $0 file_1 file_2 output_file"
  exit 1 # Exit with status code 1 to indicate an error
fi 

# Use `cat` to copy the content of the first file into the output file
cat "$1" > "$3"

# Append the content of the second file to the output file
cat "$2" >> "$3"

# Print a confirmation message indicating successful merging
echo "Merged $1 &$2 into $3"

# Display the contents of the merged output file
cat "$3"
