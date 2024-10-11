cd ~/Documents/CMEECoursework/week1/data

for input_file in *.csv;
do
# Create the output file name by replacing ".csv" with "-output.ssv"
    output_file="$result_dir/${input_file%.csv}-output.ssv"
    
    echo "Converting $input_file to $output_file..."
    tr "," " " < "$input_file" > "$output_file"
    echo "$input_file converted successfully."
done
 
echo "Processed successfully."
 

target_dir=~/Documents/CMEECourseWork/week1/data

result_dir=~/Documents/CMEECourseWork/week1/results
 
# Change to the target directory
cd "$target_dir" || { echo "Error: Unable to change to directory $target_dir."; exit 1; }
 
# Loop through all .csv files and convert them
for input_file in *.csv;
do
# Create the output file name by replacing ".csv" with "-output.ssv"
    output_file="$result_dir/${input_file%.csv}-output.ssv"
    
    echo "Converting $input_file to $output_file..."
    tr "," " " < "$input_file" > "$output_file"
    echo "$input_file converted successfully."
done
 
echo "Processed successfully."
 
 