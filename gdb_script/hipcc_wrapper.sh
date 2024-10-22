# clang_wrapper.sh
#!/bin/bash

# Get the process ID of the current script, which will be the Clang process
export RANDINT=$$

# Call the real Clang compiler with all the arguments
hipcc  -DRANDINT=$RANDINT -include ${HOME}/FloatGuard/inst_pass/Inst/InstStub.h "$@"