import os
import sys
import time
import json
import re
import pexpect
import argparse
import subprocess
import configparser
from enum import Enum
from ast import literal_eval 

if __name__ == "__main__":
    link_time = False
    argv = sys.argv
    for arg in argv:
        if arg == "--hip-link":
            link_time = True

    disable_all = True
    replaced_argv = ["hipcc"]
    for arg in argv[1:]:
        if not disable_all and arg.endswith(".o") and not "InstStub.o" in arg and os.path.exists(arg):
            arg_s = arg[:-2] + ".s"
            if not link_time:
                replaced_argv.append(arg[:-2] + ".s") 
            elif os.path.exists(arg):
                replaced_argv.append(arg[:-2] + ".s")  
            else:
                replaced_argv.append(arg)
        else:
            replaced_argv.append(arg)

    subprocess.run(replaced_argv)