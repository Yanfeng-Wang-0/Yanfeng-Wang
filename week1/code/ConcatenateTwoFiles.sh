
if [$# -ne 3] ; then
  echo "usage : $0 file_1 file_2 output_file"
  exit 1 
fi 

cat "$1" > "$3"
cat "$2" >> "$3"
echo "Merged $1 &$2 into $3"
cat "$3"
