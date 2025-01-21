#!/usr/bin/env python3
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

def process_output(captured_output):
    captured_lines = captured_output.splitlines()
    filtered_lines = []
    in_exception = False
    total_exceptions = 0
    for line in captured_lines:
        if "----------------- EXCEPTION CAPTURED -----------------" in line:
            in_exception = True
        elif "----------------- EXCEPTION CAPTURE END -----------------" in line:
            in_exception = False
            total_exceptions += 1
        elif not in_exception:
            if  not line.startswith("program:") and \
                not line.startswith("kernel name:") and \
                not line.startswith("total kernels:"):
                continue
        else:
            if line.startswith("text:"):
                continue
        filtered_lines.append(line.strip())

    return "\n".join(filtered_lines) + "\ntotal exceptions: " + str(total_exceptions) + "\n"   

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
        output += subprocess.check_output(' '.join(command), shell=True).decode() + "\n"
    totaltime = time.time() - starttime
    return totaltime, output
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, help="the directory to be tested")
    parser.add_argument("-s", "--setup", type=str, help="setup file")
    args = parser.parse_args()
    setup_file = "setup.ini"
    if args.directory:
        dir = args.directory
        if args.setup:        
            setup_file = os.path.abspath(args.setup)
    else:
        if args.setup:
            dir = os.path.dirname(os.path.abspath(args.setup))
            setup_file = os.path.abspath(args.setup)
        else:
            dir = os.getcwd()

    os.chdir(dir)
    home = str(Path.home())
    config = configparser.ConfigParser()
    config.read(setup_file)

    if 'runs' in config['DEFAULT']:
        runs = config['DEFAULT']['runs']
    else:
        runs = 1

    os.system("rm seq.txt exp_flag.txt inject_points.txt")
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
    asm_inject = True

    if asm_inject:
        # 3. if using ASM inject, compile and run program with code injection; measure time
        print("Compiling code with ASM code injection...")
        subprocess.run(compile_command, stdout=subprocess.PIPE, env={**os.environ, 'INJECT_CODE': '1'})      
    elif use_clang:
        # 2a. if using Clang plugin, convert code with the plugin
        print("Injecting code to original program with Clang plugin...")
        convert_command = config['DEFAULT']['clang_convert'].split()
        os.system(clean_command)

        # 2b. if using Clang plugin, compile and run program with code injection; measure time
        print("Compiling injected program...")

        subprocess.run(compile_command, stdout=subprocess.PIPE)
    else:
        # 3. if using LLVM pass, compile and run program with code injection; measure time
        print("Compiling code with LLVM pass code injection...")
        llvm_pass_command = config['DEFAULT']['llvm_pass'].split()
        subprocess.run(llvm_pass_command, stdout=subprocess.PIPE)

    # 4. run program with code injection with control script; measure time
    print("Running exception capture for the injected program...")
    starttime = time.time()
    capture_output = ""
    for run_command in run_command_list:
        capture_command = ['python3', '-u', os.path.join(home, "FloatGuard", "gdb_script", "exception_capture_light.py")]
        if use_clang:
            capture_command.append('-u')        
        capture_command.extend(['-p', run_command[0]])
        if len(run_command) > 1:   
            capture_command.append('-a') 
            capture_command.extend(run_command[1:])
        for path in execute(capture_command):
            capture_output += path
        #subprocess.run(capture_command)
        #capture_output = ""
    totaltime = time.time() - starttime
    time_array.append(str(totaltime))
    print("total time for exception capture:", totaltime)    

    capture_output = process_output(capture_output)

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

    num_exceptions = 0
    num_inf = 0
    num_nan = 0
    num_sub = 0
    num_div0 = 0
    for line in capture_output.splitlines():
        if "exception type: " in line:
            num_exceptions += 1
            exp_type = int(line.strip().split(":")[1].strip().split()[0])
            if exp_type == 0:
                num_nan += 1
            elif exp_type == 1 or exp_type == 4:
                num_sub += 1
            elif exp_type == 2 or exp_type == 6:
                num_div0 += 1
            elif exp_type == 3:
                num_inf += 1
    print("Total number of exceptions:", num_exceptions)
    output_array = [prog_name, prog_input, str(runs)]
    output_array.extend(time_array)
    output_array.extend([str(num_exceptions), str(num_div0), str(num_inf), str(num_nan), str(num_sub)])
    with open(os.path.join(home, "FloatGuard", "results.csv"), "a") as f:
        f.write(",".join(output_array) + "\n")

    os.system(clean_command)