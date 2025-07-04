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
        output += subprocess.check_output(' '.join(command).replace("~", os.path.expanduser("~")), shell=True).decode() + "\n"
    totaltime = time.time() - starttime
    return totaltime, output
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, help="the directory to be tested")
    parser.add_argument("-s", "--setup", type=str, help="setup file")
    parser.add_argument("-c", "--clean", dest="clean", action="store_true", help="clean mode")
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

    os.system("rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/")
    clean_command = config['DEFAULT']['clean']
    os.system(clean_command)
    time_array = []

    if args.clean:
        exit(0)

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

    # 3. if using ASM inject, compile and run program with code injection; measure time
    print("Compiling code with ASM code injection...")
    subprocess.run(compile_command, stdout=subprocess.PIPE, env={**os.environ, 'INJECT_FG_CODE': '1', 'FG_WORKDIR': dir})      

    # 4. run program with code injection with control script; measure time
    print("Running exception capture for the injected program...")
    starttime = time.time()
    capture_output = ""
    for run_command in run_command_list:
        capture_command = ['python3', '-u', os.path.join(home, "FloatGuard", "gdb_script", "exception_capture_light.py")]
        capture_command.append("-s")
        capture_command.append(setup_file)    
        capture_command.append("-d")
        capture_command.append(dir)  
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
    if setup_file != "setup.ini":
        prog_name += "_" + os.path.basename(os.path.normpath(setup_file)).replace("setup_", "").replace(".ini", "")
    if len(run_command_list) == 1:
        prog_input = "(single)"
        if len(run_command) > 1:
            prog_input = " ".join(run_command[1:])
            if len(prog_input) > 20:
                prog_input = "(single)"
        else:
            prog_input = ""
    else:
        prog_input = "(multiple)"

    with open(os.path.join(home, "FloatGuard/results", prog_name + "_output.txt"), "w") as f:
        f.write(capture_output + "\n")

    num_exceptions = 0
    num_exception_arr = [0,0,0,0,0,0,0]
    in_exception = False
    for line in capture_output.splitlines():
        if "----------------- EXCEPTION CAPTURED -----------------" in line:
            in_exception = True
        elif "----------------- EXCEPTION CAPTURE END -----------------" in line:
            num_exceptions += 1
            in_exception = False
        if in_exception and "exception type: " in line:
            exp_type = int(line.strip().split(":")[1].strip().split()[0])
            num_exception_arr[exp_type] += 1
    print("Total number of exceptions:", num_exceptions)
    output_array = [prog_name, prog_input, str(runs)]
    output_array.extend(time_array)
    output_array.extend([str(num_exceptions)])
    output_array.extend([str(i) for i in num_exception_arr])
    with open(os.path.join(home, "FloatGuard", "results.csv"), "a") as f:
        f.write(",".join(output_array) + "\n")

    os.system(clean_command)