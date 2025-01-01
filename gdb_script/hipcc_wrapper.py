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

NumInsInRange = 4

branch_keywords = ["branch_", "setpc", "swappc", "getpc", "s_call_"]

def demangle_name(name):
    result = subprocess.run(['c++filt', name], capture_output=True, text=True)
    return result.stdout.strip()

def is_branch_ins(ins):
    for branch_keyword in branch_keywords:
        if branch_keyword in ins:
            return True
        
    return False

def is_executable_compilation(command):
    # Recognize common source file extensions
    source_file_pattern = re.compile(r'.*\.(c|cpp|cxx|cc|cu|hip|C)$', re.IGNORECASE)
    source_files = [arg for arg in command if source_file_pattern.match(arg)]
    
    # Check if the command includes flags that suppress linking
    suppress_linking_flags = {'-c', '-E', '-S'}
    if any(flag in command for flag in suppress_linking_flags):
        return False, source_files
    
    # Check if the command has exactly one source file
    if len(source_files) != 1:
        return False, source_files
    
    # If `-o` is present, ensure it’s not targeting an object file or library
    if '-o' in command:
        output_index = command.index('-o') + 1
        if output_index < len(command):
            output_file = command[output_index]
            if output_file.endswith(('.o', '.so', '.a')):
                return False, source_files
    
    # If all conditions pass, it is likely compiling a single source file into an executable
    return True, source_files

if __name__ == "__main__":
    link_time = False
    compile_time = False
    clang_pass = False
    exp_flag_str = None
    has_link_param = 0
    argv = sys.argv
    for arg in argv:
        # determine link time
        if arg == "--hip-link":
            link_time = True
            has_link_param += 1
        if arg == "-fgpu-rdc":
            has_link_param += 2
        if "emit-llvm" in arg:
            clang_pass = True
        # find EXP_FLAG_TOTAL flag
        if arg.startswith("-DEXP_FLAG_TOTAL="):
            exp_flag_str = arg.strip().split("=")[1]
        if arg == "-c":
            compile_time = True

    if link_time == False and compile_time == False:
        link_time = True

    disable_all = False
    if clang_pass:
        disable_all = True

    single_source_link_time, source_files = is_executable_compilation(argv[1:])
    
    if not disable_all and single_source_link_time:
        extra_compile_argv = ["hipcc", "-c", "-S"]
        prev_is_object = False
        for arg in argv[1:]:
            if not "InstStub.o" in arg:
                if arg == "-o":
                    prev_is_object = True
                    #extra_compile_argv.append(arg)
                elif prev_is_object:
                    prev_is_object = False
                    #arg_s = arg.split(".")[0] + ".s"
                    #extra_compile_argv.append(arg_s)
                else:
                    extra_compile_argv.append(arg)

        subprocess.run(extra_compile_argv)

        # replace argv with a link-only version
        extra_compile_argv = ["hipcc"]
        for arg in argv[1:]:
            if arg in source_files:
                arg_s = arg.split(".")[0] + ".s"
                extra_compile_argv.append(arg_s)
            else:
                extra_compile_argv.append(arg)

        argv = extra_compile_argv
        link_time = True

    if exp_flag_str:
        exp_flag = int(exp_flag_str, 0)
    else:
        if link_time:
            # if link time, read EXP_FLAG_TOTAL flag from a file
            if os.path.exists("exp_flag.txt"):
                with open("exp_flag.txt", "r") as f:
                    exp_flag_str = f.readline().strip()
                    exp_flag = int(exp_flag_str, 0)
        else:     
            # no EXP_FLAG_TOTAL flag anywhere, use default
            exp_flag_str = "0x4D2F0"           
            exp_flag = 0x0004D2F0
    exp_flag_low = hex(exp_flag & 0x0000FFFF)
    exp_flag_high = hex((exp_flag & 0xFFFF0000) >> 16)
    print("exp_flag_str:", exp_flag_low, exp_flag_high)

    # read inject points
    # (kernel name, instruction index) tuples
    inject_points = []
    if link_time and os.path.exists("inject_points.txt"):
        with open("inject_points.txt", "r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if "," in line:
                    kernel_name = line.strip().split(",")[0]
                    ins_index = int(line.strip().split(",")[1])
                    inject_points.append((kernel_name, ins_index))

    build_lib = False
    replaced_argv = ["hipcc"]
    if link_time:
        if has_link_param == 0 or has_link_param == 1:
            replaced_argv.append("-fgpu-rdc")
        if has_link_param == 0 or has_link_param == 2:
            replaced_argv.append("--hip-link")
    assembly_list = []
    for arg in argv[1:]:
        if "InstStub.cpp" in arg:
            build_lib = True
        if not disable_all and arg.endswith(".o") and not "InstStub.o" in arg:
            arg_s = arg[:-2] + ".s"
            if not link_time:
                replaced_argv.append(arg_s) 
            elif os.path.exists(arg_s):
                replaced_argv.append(arg_s)  
                assembly_list.append(arg_s)
            else:
                replaced_argv.append(arg)
        else:
            replaced_argv.append(arg)

    # write EXP_FLAG_TOTAL flag if the file does not exist
    if not build_lib and not os.path.exists("exp_flag.txt"):
        with open("exp_flag.txt", "w") as f:
            f.write(exp_flag_str + "\n")

    if not disable_all and not link_time and not build_lib:
        replaced_argv.append("-S")

    if not disable_all and link_time and not build_lib and len(inject_points) > 0:
        for assembly in assembly_list:
            injected_lines = []
            # read assembly file from name
            with open(assembly, "r") as f:
                lines = f.readlines()

                prev_injected_code = False
                func_name = ""
                func_index = -1
                last_br_index = -1
                match_indices = set()
                for line in lines:
                    func_m = re.search("^([A-Za-z0-9_]+):", line)
                    if func_m:
                        func_name = ""
                        func_index = -1
                        last_br_index = -1
                        demangled_name = demangle_name(func_m.group(1))
                        print("name:", func_m.group(1), demangled_name)
                        core_name = demangled_name
                        if "(" in demangled_name:
                            core_name = demangled_name.split("(")[0]
                        for inj in inject_points:
                            kernel_name = inj[0]
                            ins_index = inj[1]
                            if kernel_name == core_name:
                                func_name = kernel_name
                                func_index = 0
                                match_indices.add(ins_index) 
                        injected_lines.append(line)
                        continue  

                    if func_name == "":
                        injected_lines.append(line)
                        continue             

                    written_ins = False        

                    if "s_endpgm" in line:
                        func_name = ""
                        func_index = -1
                        last_br_index = -1
                        match_indices = set()
                    elif "; injected code start" in line:
                        print(line.strip())
                        prev_injected_code = True
                    elif "; injected code end" in line:
                        if func_index >= 0:
                            func_index += 1
                        print(line.strip())
                        prev_injected_code = False
                    elif not line.strip().startswith(";") and not line.strip().startswith("."):
                        if not prev_injected_code:
                            if is_branch_ins(line):
                                last_br_index = len(injected_lines) + 1
                            elif "s_setreg_b32" in line:
                                last_br_index = len(injected_lines) + 1
                            for index in match_indices:
                                if index == func_index:
                                    if last_br_index == -1:
                                        injected_lines.append("; injected code start\n")
                                        injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), 0x2F0\n")
                                        injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), 0\n")                                                                                   
                                    else:
                                        injected_lines.insert(last_br_index, "\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), 0\n")
                                        injected_lines.insert(last_br_index, "\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), 0x2F0\n")
                                        injected_lines.insert(last_br_index, "; injected code start\n")

                                    injected_lines.append(line)
                                    print("injected line:", line.strip())
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), " + exp_flag_low + "\n")
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), " + exp_flag_high + "\n")
                                    injected_lines.append("; injected code end\n")  
                                    written_ins = True
                                #if index - func_index == NumInsInRange:                               
                                #    injected_lines.append("; injected code start\n")
                                #    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), 0x2F0\n")
                                #    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), 0\n")                                    
                                #elif index - func_index == 0:
                                #    injected_lines.append(line)
                                #    print("injected line:", line.strip())
                                #    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), " + exp_flag_low + "\n")
                                #    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), " + exp_flag_high + "\n")
                                #    injected_lines.append("; injected code end\n")
                                #    written_ins = True
                            if func_index >= 0:
                                func_index += 1
                    elif line.strip().startswith(".LBB"):
                        # start of a basic block
                        last_br_index = len(injected_lines) + 1
                    if written_ins:
                        last_br_index = len(injected_lines)
                    else:
                        injected_lines.append(line)

            if len(injected_lines) > 0:
                with open(assembly, "w") as f:
                    f.writelines(injected_lines)

    subprocess.run(replaced_argv)   