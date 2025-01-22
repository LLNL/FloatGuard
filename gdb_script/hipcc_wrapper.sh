#!/bin/bash
# clang_wrapper.sh

# Get the process ID of the current script, which will be the Clang process
export RANDINT=$$
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Call the real Clang compiler with all the arguments
python3 $SCRIPT_DIR/hipcc_wrapper.py "$@"