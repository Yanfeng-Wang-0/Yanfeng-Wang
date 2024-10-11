cd ~/Documents/CMEECoursework/week1/data

#ensure at least 1 file exist and warning if not 
if [ $# -lt 1 ]; then
  echo "Please provide at least one CSV file."
  exit 1
fi

result_dir=~/Documents/CMEECoursework/week1/results

#creat output file and rename it
for input_file in "$@"; do
  output_file="$result_dir/${input_file%.csv}_output.ssv"

  sed 's/,/ /g' "$input_file" > "$output_file"
  tr "," " " < "$input_file" > "$out_file"

  echo "Converted $input_file to $output_file"
done