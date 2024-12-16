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

def demangle_name(name):
    result = subprocess.run(['c++filt', name], capture_output=True, text=True)
    return result.stdout.strip()

if __name__ == "__main__":
    link_time = False
    exp_flag_str = None
    argv = sys.argv
    for arg in argv:
        # determine link time
        if arg == "--hip-link":
            link_time = True
        # find EXP_FLAG_TOTAL flag
        if arg.startswith("-DEXP_FLAG_TOTAL="):
            exp_flag_str = arg.strip().split("=")[1]

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
    exp_flag_low = str(exp_flag & 0x0000FFFF)
    exp_flag_high = str((exp_flag & 0xFFFF0000) >> 16)
    print("exp_flag_str:", exp_flag_low, exp_flag_high)

    # write EXP_FLAG_TOTAL flag if the file does not exist
    if not os.path.exists("exp_flag.txt"):
        with open("exp_flag.txt", "w") as f:
            f.write(exp_flag_str + "\n")

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

    disable_all = False
    build_lib = False
    replaced_argv = ["hipcc"]
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
                match_indices = set()
                for line in lines:
                    func_m = re.search("^([A-Za-z0-9_]+):", line)
                    if func_m:
                        func_name = ""
                        func_index = -1
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

                    if "s_endpgm" in line:
                        func_name = ""
                        func_index = -1
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
                            if func_index in match_indices:
                                injected_lines.append("; injected code start\n")
                                injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), 0x2F0\n")
                                injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), 0\n")
                                injected_lines.append(line)
                                print("injected line:", line.strip())
                                injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), " + exp_flag_low + "\n")
                                injected_lines.append("\ts_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), " + exp_flag_high + "\n")
                                injected_lines.append("; injected code end\n")
                            if func_index >= 0:
                                func_index += 1
                    injected_lines.append(line)

            if len(injected_lines) > 0:
                with open(assembly, "w") as f:
                    f.writelines(injected_lines)

    subprocess.run(replaced_argv)   