#!/bin/bash

# Script to compile an lf file and trace its execution
bnry_dir=$(lfc -c  "$1" | grep -o 'binary is in.*' | cut -d ' ' -f 4)

# Remove .lf from end of string
v=$1
rem_extension=${v::-3}

# Extract program name from input filepath
bnry_name=$(echo $rem_extension | rev | cut -d '/' -f 1 | rev)

# Concat dir with filename
bnry_path="$bnry_dir/$bnry_name"

# Start tracing, execute binary and stop trace
trace_dir=$(/bin/bash start_tracing.sh | grep -o 'Traces will be output to.*' | cut -d ' ' -f 6)
$bnry_path
/bin/bash stop_tracing.sh

# pass all but the first argument to python
python ../main.py $trace_dir $bnry_name.yaml "${@:2}"

rm $bnry_name.yaml
