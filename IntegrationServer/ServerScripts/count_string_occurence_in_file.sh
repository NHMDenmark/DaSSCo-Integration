#!/bin/bash

# Check if both arguments are provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <search_string> <file_path>"
    exit 1
fi

search_string="$1"
file_path="$2"

# Check if the file exists
if [ ! -f "$file_path" ]; then
    echo "Error: File '$file_path' not found!"
    exit 1
fi

# Count occurrences of the string in the file
count=$(grep -o "$search_string" "$file_path" | wc -l)

# Output the result
echo "The string '$search_string' appears $count times in '$file_path'."
