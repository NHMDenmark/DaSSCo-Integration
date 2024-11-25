#!/bin/bash

# takes argument of a file path to a .py file with docstrings and prints the docstrings to the output file. 

file_path="$1"

output_file="/work/data/Dev-Integration/DaSSCo-Integration/docstring.out" 

/work/data/integration/venv_integration/bin/python -m pydoc "$file_path" > "$output_file"