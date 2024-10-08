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
from pathlib import Path

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

def run_commands(commands):
    starttime = time.time()
    output = ""
    for command in commands:
        output += subprocess.check_output(command).decode() + "\n"
    totaltime = time.time() - starttime
    return totaltime, output
    
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--directory", type=str, help="the directory to be tested", required=True)
        args = parser.parse_args()
        dir = args.directory
    else:
        dir = os.getcwd()
    os.chdir(dir)
    home = str(Path.home())
    config = configparser.ConfigParser()
    config.read("setup.ini")

    if 'runs' in config['DEFAULT']:
        runs = config['DEFAULT']['runs']
    else:
        runs = 1

    os.system("rm seq.txt")
    clean_command = config['DEFAULT']['clean']
    os.system(clean_command)
    time_array = []

    # 1. compile and run the program without code injection; measure time
    print("Compiling original program...")
    compile_command = config['DEFAULT']['compile'].split()
    run_command_str = config['DEFAULT']['run'].split(';')
    run_command_list = []
    for cmd in run_command_str:
        run_command_list.append(cmd.split())

    subprocess.run(compile_command, stdout=subprocess.PIPE)
    print("Running original program...")
    if not 'runtime_method' in config['DEFAULT']:
        totaltime, output = run_commands(run_command_list)
        print("total time for original program:", totaltime)
        time_array.append(str(totaltime))

    os.system(clean_command)

    # 2. detect to use Clang plugin or LLVM pass
    use_clang = config['DEFAULT'].getboolean('use_clang_plugin')

    if use_clang:
        # 2a. if using Clang plugin, convert code with the plugin
        print("Injecting code to original program with Clang plugin...")
        convert_command = config['DEFAULT']['clang_convert'].split()
        subprocess.run(convert_command, stdout=subprocess.PIPE)
        os.system(clean_command)

        # 2b. if using Clang plugin, compile and run program with code injection; measure time
        print("Compiling injected program...")

        subprocess.run(compile_command, stdout=subprocess.PIPE)
        print("Running injected program...")
        totaltime, output = run_commands(run_command_list)
        time_array.append(str(totaltime))
        print("total time for injected program:", totaltime)
    else:
        # 3. if using LLVM pass, compile and run program with code injection; measure time
        print("Compiling code with LLVM pass code injection...")
        llvm_pass_command = config['DEFAULT']['llvm_pass'].split()
        subprocess.run(llvm_pass_command, stdout=subprocess.PIPE)

        totaltime, output = run_commands(run_command_list)
        time_array.append(str(totaltime))
        print("total time for injected program:", totaltime)

    # 4. run program with code injection with control script; measure time
    print("Running exception capture for the injected program...")
    starttime = time.time()
    capture_output = ""
    for run_command in run_command_list:
        capture_command = ['python3', '-u', os.path.join(home, "FloatGuard", "gdb_script", "exception_capture_light.py")]
        capture_command.extend(['-p', run_command[0]])
        if len(run_command) > 1:   
            capture_command.append('-a') 
            capture_command.extend(run_command[1:])
        # Example
        for path in execute(capture_command):
            capture_output += path
            #print(path, end="")
        #output = subprocess.check_output(capture_command).decode()
    totaltime = time.time() - starttime
    time_array.append(str(totaltime))
    print("total time for exception capture:", totaltime)    

    prog_name = os.path.basename(os.path.normpath(dir))
    if len(run_command_list) == 1:
        if len(run_command) > 1:
            prog_input = " ".join(run_command[1:])
        else:
            prog_input = ""
    else:
        prog_input = "(multiple)"

    with open(os.path.join(home, "FloatGuard", prog_name + "_output.txt"), "w") as f:
        f.write(capture_output + "\n")

    num_exceptions = capture_output.count("EXCEPTION CAPTURED")
    print("number of exceptions found:", num_exceptions)
    
    output_array = [prog_name, prog_input, str(runs)]
    output_array.extend(time_array)
    output_array.append(str(num_exceptions))
    with open(os.path.join(home, "FloatGuard", "results.csv"), "a") as f:
        f.write(",".join(output_array) + "\n")

    os.system(clean_command)