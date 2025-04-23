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

def code_injection_top(asm_file):
    inside_hip_region = False
    inside_function = False
    code_injected_in_function = False
    print("initial code injection:", asm_file)
    with open(asm_file, "r", encoding='latin1') as f:
        lines = f.readlines()

    injected_lines = []
    for index, line in enumerate(lines):
        if "hip-amdgcn-amd-amdhsa" in line:
            if "__CLANG_OFFLOAD_BUNDLE____START__" in line:
                inside_hip_region = True
            elif "__CLANG_OFFLOAD_BUNDLE____END__" in line:
                inside_hip_region = False
        elif inside_hip_region:
            func_m = re.search("^([A-Za-z0-9_]+):", line)
            if not inside_function and func_m and lines[index-1].strip().endswith("@function"):
                inside_function = True
                code_injected_in_function = False
                print("find function begin 1")                
            elif not inside_function and line.startswith(".Lfunc_begin"):
                inside_function = True
                code_injected_in_function = False
                print("find function begin 2")
            elif "s_endpgm" in line or line.startswith(".Lfunc_end"):
                inside_function = False
                code_injected_in_function = False
                print("find function end")
            elif inside_function:
                if not code_injected_in_function and line.strip() != "" and not line.strip().startswith(";") and not line.strip().startswith("."):                    
                    #injected_lines.append("\ts_mov_b32 s31, s0\n")
                    injected_lines.append("\ts_mov_b32 s31, 0x5F2F0\n")
                    injected_lines.append("\ts_setreg_b32 hwreg(HW_REG_MODE), s31\n")
                    #injected_lines.append("\ts_mov_b32 s0, s31\n")
                    code_injected_in_function = True                                      
        injected_lines.append(line)

    with open(asm_file, "w") as f:
        f.writelines(injected_lines)
    return

if __name__ == "__main__":
    link_time = False
    compile_time = False
    clang_pass = False
    exp_flag_str = None
    has_link_param = 0
    argv = sys.argv
    fg_work_dir = os.getenv("FG_WORKDIR", default=os.getcwd())
    hip_clang_path = os.getenv("HIP_CLANG_PATH", default="/opt/rocm/llvm/bin")
    copy_argv = []
    for arg in argv:
        if arg == hip_clang_path:
            continue
        # determine link time
        if arg == "--hip-link":
            link_time = True
            has_link_param += 1
        if arg == "-fgpu-rdc":
            has_link_param += 2
        if "emit-llvm" in arg or "-M" in arg:
            clang_pass = True
        # find EXP_FLAG_TOTAL flag
        if arg.startswith("-DEXP_FLAG_TOTAL="):
            exp_flag_str = arg.strip().split("=")[1]
        if arg == "-c":
            compile_time = True
        copy_argv.append(arg)
    argv = copy_argv

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
                elif not "fgpu-rdc" in arg and not "hip-link" in arg:
                    extra_compile_argv.append(arg)

        print("initial run:", " ".join(extra_compile_argv))
        subprocess.run(extra_compile_argv)

        # replace argv with a link-only version
        extra_compile_argv = [os.path.abspath(__file__)]
        first_object = True
        for arg in argv[1:]:
            if arg in source_files:
                if first_object:
                    #extra_compile_argv.append(os.path.join(os.path.expanduser("~"), "FloatGuard/inst_pass/Inst/InstStub.o"))
                    first_object = False
                arg_s = arg.split(".")[0] + ".o"
                extra_compile_argv.append(arg_s)
            else:
                extra_compile_argv.append(arg)

        argv = extra_compile_argv
        link_time = True

    # inject initial code first
    inject_code = os.getenv('INJECT_FG_CODE', 0)
    print(f"INJECT_FG_CODE in inner Python script: {inject_code}")

    if exp_flag_str:
        exp_flag = int(exp_flag_str, 0)
    else:
        # if link time, read EXP_FLAG_TOTAL flag from a file
        if link_time and os.path.exists(os.path.join(fg_work_dir, "exp_flag.txt")):
                with open(os.path.join(fg_work_dir, "exp_flag.txt"), "r") as f:
                    exp_flag_str = f.readline().strip()
                    exp_flag = int(exp_flag_str, 0)
        else:     
            # no EXP_FLAG_TOTAL flag anywhere, use default
            exp_flag_str = "0x5F2F0"           
            exp_flag = 0x0005F2F0
    exp_flag_low = hex(exp_flag & 0x0000FFFF)
    exp_flag_high = hex((exp_flag & 0xFFFF0000) >> 16)
    print("exp_flag_str:", exp_flag_low, exp_flag_high)

    # read inject points
    # (kernel name, instruction index) tuples
    inject_points = []
    if link_time and os.path.exists(os.path.join(fg_work_dir, "inject_points.txt")):
        with open(os.path.join(fg_work_dir, "inject_points.txt"), "r") as f:
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
    first_object = True
    for arg in argv[1:]:
        if "InstStub.cpp" in arg:
            build_lib = True
        if not disable_all and arg.endswith(".o") and not "InstStub.o" in arg:
            if link_time and first_object:
                #replaced_argv.append(os.path.join(os.path.expanduser("~"), "FloatGuard/inst_pass/Inst/InstStub.o"))
                first_object = False
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

    # if first time, store asm
    if not disable_all and link_time and not build_lib and inject_code != 0:
        if os.path.exists(os.path.join(fg_work_dir, "asm_info")):
            with open(os.path.join(fg_work_dir, "asm_info/link_command.txt"), "r") as f:
                lines = f.readlines()
            for line in lines[2:]:
                asm_file = line.strip()
                print("read assembly file:", asm_file)
                os.system("cp " + os.path.join(fg_work_dir, "asm_info", os.path.basename(asm_file)) + " " + os.path.dirname(os.path.abspath(asm_file)))
        else:
            # basic injection at the beginning. then save the assembly
            for asm_file in assembly_list:
                code_injection_top(asm_file)
            os.mkdir(os.path.join(fg_work_dir, "asm_info"))
            with open(os.path.join(fg_work_dir, "asm_info/link_command.txt"), "w") as f:
                f.write(" ".join(argv) + "\n")
                f.write(os.getcwd() + "\n")
                for asm_file in assembly_list:
                    f.write(asm_file + "\n")
                    os.system("cp " + os.path.abspath(asm_file) + " " + os.path.join(fg_work_dir, "asm_info"))

    # write EXP_FLAG_TOTAL flag if the file does not exist
    if not build_lib and inject_code != 0 and not os.path.exists(os.path.join(fg_work_dir, "exp_flag.txt")):
        with open(os.path.join(fg_work_dir, "exp_flag.txt"), "w") as f:
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
                last_insert_index = -1
                last_br_index = -1
                last_br_func_index = -1
                match_indices = set()
                for line in lines:
                    func_m = re.search("^([A-Za-z0-9_]+):", line)
                    if func_m:
                        func_name = ""
                        func_index = -1
                        last_insert_index = -1
                        last_br_index = -1
                        last_br_func_index = -1
                        demangled_name = demangle_name(func_m.group(1))
                        core_name = demangled_name
                        func_core_m = re.search("^(?:[A-Za-z0-9_<>:]+\s+)?([A-Za-z0-9_<>:]+)", demangled_name)
                        if func_core_m:
                            core_name = func_core_m.group(1)
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
                        last_insert_index = -1
                        last_br_index = -1
                        last_br_func_index = -1
                        match_indices = set()
                    elif "; injected code start" in line:
                        print(line.strip())
                        prev_injected_code = True
                    elif "; injected code end" in line:
                        print(line.strip())
                        prev_injected_code = False
                    elif not line.strip().startswith(";") and not line.strip().startswith("."):
                        is_nop = "s_nop" in line
                        if prev_injected_code:
                            if not "s_setreg_imm32_b32 hwreg(HW_REG_TRAPSTS" in line and \
                               not "s_setreg_imm32_b32 hwreg(HW_REG_MODE" in line:
                                if not is_nop and func_index >= 0:
                                    func_index += 1                            
                        else:
                            ins_to_disable = func_index in match_indices
                            is_branch = is_branch_ins(line)
                            if not ins_to_disable:
                                if is_branch:
                                    last_insert_index = len(injected_lines) + 1
                                    last_br_index = last_insert_index - 1
                                    last_br_func_index = func_index
                                elif "s_setreg_b32" in line:
                                    last_insert_index = len(injected_lines) + 1
                            else:                                                      
                                if last_insert_index == -1:
                                    injected_lines.append("; injected code start\n")
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), 0x2F0\n")
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), 0\n")          
                                else:
                                    injected_lines.insert(last_insert_index, "\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), 0\n")
                                    injected_lines.insert(last_insert_index, "\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), 0x2F0\n")
                                    injected_lines.insert(last_insert_index, "; injected code start\n")

                                # crash location too close to branch; could be instruction before branch that cause issues
                                print("current index, last_br_index:", func_index, last_br_func_index)
                                if func_index - last_br_func_index <= NumInsInRange:               
                                    injected_lines.insert(last_br_index, "; injected code end\n")                                           
                                    injected_lines.insert(last_br_index, "\ts_setreg_imm32_b32 hwreg(HW_REG_TRAPSTS, 0, 9), 0\n")                                                                                   
                                    injected_lines.insert(last_br_index, "\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), " + exp_flag_low + "\n")
                                    injected_lines.insert(last_br_index, "\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), " + exp_flag_high + "\n")                                        
                                    injected_lines.insert(last_br_index - NumInsInRange, "\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), 0\n")
                                    injected_lines.insert(last_br_index - NumInsInRange, "\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), 0x2F0\n")
                                    injected_lines.insert(last_br_index - NumInsInRange, "; injected code start\n")           

                                if is_branch:
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_TRAPSTS, 0, 9), 0\n")                                                                                   
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), " + exp_flag_low + "\n")
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), " + exp_flag_high + "\n")
                                    injected_lines.append("; injected code end\n")   
                                    injected_lines.append(line)#.rstrip() + "\t; " + str(func_index) + "\n")
                                    print("injected line:", line.strip())                                                                      
                                else:
                                    injected_lines.append(line)#.rstrip() + "\t; " + str(func_index) + "\n")
                                    print("injected line:", line.strip())
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_TRAPSTS, 0, 9), 0\n")                                                                                   
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), " + exp_flag_low + "\n")
                                    injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), " + exp_flag_high + "\n")
                                    injected_lines.append("; injected code end\n")  
                                written_ins = True
                                last_insert_index = len(injected_lines)
                            if not is_nop and func_index >= 0:
                                func_index += 1
                        if not written_ins:
                            injected_lines.append(line)#.rstrip() + "\t; " + str(func_index - 1) + "\n")
                        continue
                    elif line.strip().startswith(".LBB"):
                        # start of a basic block
                        last_insert_index = len(injected_lines) + 1
                        last_br_index = last_insert_index - 1
                        last_br_func_index = func_index                        
                    injected_lines.append(line)

            if len(injected_lines) > 0:
                with open(assembly, "w") as f:
                    f.writelines(injected_lines)

    print("final run:", " ".join(replaced_argv))
    subprocess.run(replaced_argv)   