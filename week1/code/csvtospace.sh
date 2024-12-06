# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: csvtospace.sh
# Description: convert .csv to .ssv
# Version: 0.0.1
# Date: Oct 2024

# Navigate to the target directory containing CSV files
cd ~/Documents/CMEECoursework/week1/data

# Loop through all CSV files in the current directory
for input_file in *.csv;
do
    # Define the output file path in the results directory, replacing `.csv` with `-output.ssv`
    output_file="$result_dir/${input_file%.csv}-output.ssv"
    
    # Print the current conversion task
    echo "Converting $input_file to $output_file..."

    # Replace commas with spaces in the input file and save to the output file
    tr "," " " < "$input_file" > "$output_file"

    # Confirm successful conversion
    echo "$input_file converted successfully."
done
 
echo "Processed successfully."
 
# Define the target directory containing CSV files
target_dir=~/Documents/CMEECourseWork/week1/data

# Define the directory where the converted files will be saved
result_dir=~/Documents/CMEECourseWork/week1/results
 
# Change to the target directory or exit with an error message if the directory doesn't exist
cd "$target_dir" || { echo "Error: Unable to change to directory $target_dir."; exit 1; }

# Loop through all CSV files in the target directory
for input_file in *.csv;
do
    # Create the output file path by replacing `.csv` with `-output.ssv`
    output_file="$result_dir/${input_file%.csv}-output.ssv"
    
    # Inform the user about the current conversion process
    echo "Converting $input_file to $output_file..."

    # Replace commas with spaces in the input file and save to the output file
    tr "," " " < "$input_file" > "$output_file"

    # Confirm successful conversion
    echo "$input_file converted successfully."
done

# Final message indicating all files have been processed
echo "Processed successfully."
 
 