#!/bin/bash

echo $PATH
# Script to compile an lf file and trace its execution
bnry_dir=$(lfc -c  "$1" | grep -o 'binary is in.*' | cut -d ' ' -f 4)

echo "bnry_dir: "
# Remove .lf from end of string
v=$1
rem_extension=${v::-3}

# Extract program name from input filepath
bnry_name=$(echo $rem_extension | rev | cut -d '/' -f 1 | rev)

echo "binary name: "
echo $bnry_name

# Concat dir with filename
bnry_path="$bnry_dir/$bnry_name"

echo "bnry_path: "
echo $bnry_path

# Start tracing, execute binary and stop trace
trace_dir=$(/bin/bash start_tracing.sh | grep -o 'Traces will be output to.*' | cut -d ' ' -f 6)
$bnry_path
/bin/bash stop_tracing.sh

echo "trace dir: "
echo $trace_dir
/bin/bash ctf_to_json.py $trace_dir

mv trace.json $bnry_name.json

/bin/bash ../visualiser.py $bnry_name.json $bnry_name.yaml

rm $bnry_name.json $bnry_name.yaml