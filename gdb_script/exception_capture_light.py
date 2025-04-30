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
import hashlib
from enum import Enum
from ast import literal_eval 

skipFunctionList = ["pow", "cbrt", "sqrtf64"]

PrintPrintf = False
PrintTrace = False
PrintCurInst = False

StepLine = True 

NumInjectedLines = 5

class FPType(Enum):
    ScalarSingle = 0
    ScalarDouble = 1
    PackedSingle = 2
    PackedDouble = 3
    PackedBitwise = 4

PackedBitwise = set(["pand", "pandn", "por", "pxor"])

IconText = ["\\", "|", "/", "-"]

count = 0
Verbose = 2
LastParam = -1

def prt(*args, **kwargs):
    # level 0 - 3: error, warning, info, low-priority info
    # default prt level: info (2)
    global Verbose
    level = 3
    if "level" in kwargs:
        level = kwargs["level"]
        kwargs.pop("level")
    if Verbose >= level:
        print(*args, **kwargs)

def recv(gdb, display):
    gdb.expect(r'\(gdb\)')
    text = gdb.before.decode('utf-8')
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    if display:
        prt("text:", text, level=2)
    return text

def send(gdb, *txt, **kwargs):
    global count
    count += 1
    display = False
    if "display" in kwargs:
        display = kwargs["display"]

    sendText = ' '.join(txt)
    prt("send:", sendText, level=3)
    gdb.sendline(sendText)
    #time.sleep(0.001)
    allText = recv(gdb, display)
    if sendText.startswith("r ") or sendText.startswith("sig ") or sendText == "c":
        extract_stdout(allText)
    return allText

def extract_stdout(text):
    lines = text.splitlines()
    for line in lines:
        if "Continuing with no signal." in line:
            continue
        if "hit Breakpoint" in line:
            break
        if "hit Temporary breakpoint" in line:
            break        
        if "Continuing." in line:
            continue
        if "Arithmetic exception." in line:
            break
        if "The program is not being run" in line:
            break
        if "[AMDGPU Wave " in line or "[Switching to thread " in line or "[Thread debugging using" in line or "[New Thread " in line:
            continue
        if line.startswith("r ") or line.startswith("sig") or line.strip() == "sig 0" or line.strip() == "c" or line.strip() == "":
            continue
        prt(line.strip(), level=1)

def PrintAddr(fptype, addr):
    if fptype == FPType.PackedBitwise:
        regText = send("x/4x", str(addr))
        return regText.splitlines()[-1].split(":")[1].strip().replace("\t", " ")
    elif fptype == FPType.ScalarSingle:
        regText = send("x/4f", str(addr))
        return regText.splitlines()[-1].split(":")[1].strip().split()[0]
    elif fptype == FPType.ScalarDouble:
        regText = send("x/2fg", str(addr))
        return regText.splitlines()[-1].split(":")[1].strip().split()[0]     
    elif fptype == FPType.PackedSingle:
        regText = send("x/4f", str(addr))
        return regText.splitlines()[-1].split(":")[1].strip().replace("\t", " ")
    elif fptype == FPType.PackedDouble:
        regText = send("x/2fg", str(addr))
        return regText.splitlines()[-1].split(":")[1].strip().replace("\t", " ")              

def extract_kernel_names(name):
    kernels = set()
    hipcc_rocm_path = os.path.realpath(subprocess.check_output(["which", "hipcc"]).decode().strip()).replace("/bin/hipcc", "")
    disasm = subprocess.check_output([hipcc_rocm_path + "/llvm/bin/llvm-objdump", "-d", "--demangle", name]).decode()
    lines = disasm.splitlines()    
    for line in lines:
        m = re.search("[0-9a-f]+\s<(__device_stub__[A-Za-z0-9_]+)\([^\)]*\)>:", line)
        if m:
            kernels.add(m.group(1))       
        m = re.search("[0-9a-f]+\s<void\s(__device_stub__[A-Za-z0-9_]+)", line)
        if m:         
            kernels.add(m.group(1))         
    return kernels

def send_param(gdb, param):
    global LastParam
    if LastParam != param:
        send(gdb, "p param=" + str(param))
        LastParam = param

def get_address_from_line(line):
    match = re.search(r'0x[0-9a-fA-F]+', line)
    return int(match.group(0), 16) if match else float('inf')

def get_key_from_kernel_ins_tuple(inj):
    sha1_hash = hashlib.sha1(inj[0].encode('utf-8')).hexdigest()
    sha1_num_hash = int(sha1_hash[:8], 16)
    return (sha1_num_hash << 32) + inj[1]

def is_set_mode_trapsts_reg(line):
    return "s_setreg_imm32_b32 hwreg(HW_REG_MODE" in line or "s_setreg_imm32_b32 hwreg(HW_REG_TRAPSTS" in line

def test_program(program_name, kernel_names, orig_kernel_seq, saved_rips, saved_locs, kernel_disassemble, injected_points):
    gdb = pexpect.spawn('rocgdb', timeout=3600)
    gdb.delaybeforesend = None
    gdb.delayafterread = None
    gdb.delayafterclose = None
    gdb.delayafterterminate = None    
    kernel_seq = []
    saved_rip_seq = []
    recv(gdb, False)
    send(gdb, "set", "pagination", "off")
    send(gdb, "set", "print", "asm-demangle", "on")
    send(gdb, "set", "disassemble-next-line", "on")
    send(gdb, "set", "breakpoint", "pending", "on")
    send(gdb, "set", "style", "enabled", "off")
    
    send(gdb, "file", program_name)

    # write kernel seq and saved rips to file
    seq_file = os.path.join(os.getcwd(), "seq.txt")
    with open(seq_file, "w") as f:
        f.write(str(len(orig_kernel_seq)) + "\n")
        f.write(str(len(saved_rips)) + "\n")
        for rip in saved_rips:
            f.write(rip + "\n")
    
    loc_file = os.path.join(os.getcwd(), "loc.txt")
    with open(loc_file, "w") as f:
        f.write(str(len(saved_locs)) + "\n")
        for loc in saved_locs:
            f.write(loc+ "\n")

    if len(injected_points) > 0:
        inj_file = os.path.join(os.path.join(dir, "inject_points.txt"))
        with open(inj_file, "w") as f:
            for inj in injected_points:
                f.write(inj[0] + "," + str(inj[1]) + "\n")

        # recompile the program
        # NEW: rerun the linker only
        if os.path.exists("asm_info/link_command.txt"):
            with open("asm_info/link_command.txt", "r") as f:
                linker_command = f.readline().replace("${HOME}", os.path.expanduser("~"))
                linker_dir = f.readline()
                subprocess.run(linker_command.strip().split(), cwd=linker_dir.strip(), env={**os.environ, 'INJECT_FG_CODE': '1', 'FG_WORKDIR': dir})
                #os.system(linker_command.strip())
        else:
            clean_command = conf['DEFAULT']['clean']
            os.system(clean_command)        
            if use_clang:
                compile_command = conf['DEFAULT']['compile'].split()
                subprocess.run(compile_command, stdout=subprocess.PIPE)            
            else:
                llvm_pass_command = conf['DEFAULT']['llvm_pass'].split()
                subprocess.run(llvm_pass_command, stdout=subprocess.PIPE)

    #for kernel in kernel_names:
    #    send(gdb, "b", kernel)
    #send(gdb, "b", "set_fp_exception_enabled")
    
    if Arguments:
        output = send(gdb, "r", *Arguments)
    else:
        output = send(gdb, "r")    

    timeCount = time.time()
    if "received signal" in output:
        if "SIGABRT" in output:
            print("abort! 3")
            gdb.close()
            return kernel_seq, saved_rips, saved_locs, kernel_disassemble, injected_points, True
        if "Arithmetic exception" in output:
            outlines = output.splitlines()
            startcopy = False
            filename = "(none)"
            line_number = -1
            error_loc = "(none)"
            print("----------------- EXCEPTION CAPTURED -----------------")
            for line in outlines:
                pattern = r'at\s+([\w\.\/\-]+):(\d+)'
                match = re.search(pattern, line)
                if match:
                    filename = match.group(1)
                    line_number = match.group(2)
                    print(f"File: {filename}, Line: {line_number}")
                # math library, get upper level
                while "/opt/rocm" in filename:
                    up_text = send(gdb, "up")
                    if "you cannot go up" in up_text:
                        break
                    up_outlines = up_text.splitlines()
                    for line in up_outlines:
                        pattern = r'at\s+([\w\.\/\-]+):(\d+)'
                        match = re.search(pattern, line)
                        if match:
                            filename = match.group(1)
                            line_number = match.group(2)
                            print(f"File: {filename}, Line: {line_number}")

                match = re.search(r'=>\s+(0x[0-9a-fA-F]+)', line)
                if match:
                    error_loc = match.group(1)
                    error_loc = "0x" + error_loc.replace("0x", "").zfill(16)
                    print("error loc:", error_loc)
            if error_loc == "(none)":
                error_loc_lines = send(gdb, "x/i", "$pc").splitlines()
                for line in error_loc_lines:
                    match = re.search(r'=>\s+(0x[0-9a-fA-F]+)', line)
                    if match:
                        error_loc = match.group(1)
                        error_loc = "0x" + error_loc.replace("0x", "").zfill(16)
                        print("error loc:", error_loc)                    
            trapsts = (int)(send(gdb, "p", "$trapsts&0x1ff").strip().split("=")[1].strip()) & exception_flags
            if trapsts & 0x01:
                print("exception type: 0 invalid")
            if trapsts & 0x02:
                print("exception type: 1 input denormal")                                
            if trapsts & 0x04:
                print("exception type: 2 divide by zero")
            if trapsts & 0x08:
                print("exception type: 3 overflow")
            if trapsts & 0x10:
                print("exception type: 4 underflow")
            #if trapsts & 0x20:
            #    print("exception type: 5 inexact")
            if trapsts & 0x40:
                print("exception type: 6 integer divide by zero")
            bt_list = send(gdb, "bt", display=True).splitlines()
            idx = len(bt_list) - 1
            while idx >= 0:
                line = bt_list[idx].strip()
                m = re.search("#[0-9]+\s+(?:0x[0-9a-f]+\s+in\s)?([a-zA-Z0-9_<>]+)", line)
                if m:
                    exception_kernel_name = m.group(1)
                    break
                idx -= 1         
            #print("exception kernel name:", exception_kernel_name)              
            for idx in range(8):
                func_name = send(gdb, "p", "current_func[" + str(idx) + "]")
                if "__device_stub__" + exception_kernel_name + "(" in func_name:
                    rips_text = send(gdb, "p/x", "current_rips[" + str(idx) + "]").splitlines()[-1].strip().split()[-1]
                    saved_rips.append(rips_text)
                    break
            saved_locs.append(filename + ":" + str(line_number))
            kernel_disassemble[exception_kernel_name] = send(gdb, "disassemble", exception_kernel_name).replace("=>", "  ").splitlines()
            #print(send(gdb, "disassemble", exception_kernel_name), file=open(exception_kernel_name + ".dump", "w"))
            ins_index = 0
            ins_strings = []
            for line in kernel_disassemble[exception_kernel_name]:
                match = re.search(r'^\s*(0x[0-9a-fA-F]+)', line)
                if match:
                    ins_strings.append(line)
            ins_strings = sorted(ins_strings, key=get_address_from_line)
            #print(*ins_strings, sep="\n")
            for idx, line in enumerate(ins_strings):
                if error_loc in line:
                    if is_set_mode_trapsts_reg(line):
                        ins_index -= 1
                        if is_set_mode_trapsts_reg(ins_strings[idx-1]):
                            ins_index -= 1
                    break
                if not "s_nop" in line and not is_set_mode_trapsts_reg(line):
                    ins_index += 1
            #print("ins_index_old:", ins_index)
            # adjustment from previous injected code

            injected_points.append((exception_kernel_name, ins_index))
            injected_points = sorted(injected_points, key=get_key_from_kernel_ins_tuple)

            print("ins_index:", ins_index)
            print("----------------- EXCEPTION CAPTURE END -----------------")     

            #while True:
            #    instr = input("(gdb) ")
            #    if instr.strip() == "skip":
            #        break
            #    else:
            #        send(gdb, instr, display=True)

            gdb.close()

            return kernel_seq, saved_rips, saved_locs, kernel_disassemble, injected_points, False
        else:
            print("other exceptions?") 
            print("-----------------")
            print("exception text:", output)
            print("-----------------")                                                                           
    output = send(gdb, "c")
    if "The program is not being run" in output:
        print("abort! 4")

    gdb.close()
    return kernel_seq, saved_rips, saved_locs, kernel_disassemble, injected_points, True

if __name__ == "__main__":
    if StepLine:
        PrintPrintf = False
        PrintTrace = False
        PrintCurInst = False
   
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interactive", dest='interactive', action='store_true', help='Interactive mode')
    parser.add_argument("-d", "--directory", type=str, help="Directory to be tested")
    parser.add_argument("-s", "--setup", dest="setup", type=str, help="Setup file path")
    parser.add_argument("-p", "--program", type=str, help="Program to be tested", required=True)
    parser.add_argument("-a", "--args", nargs='*', help="Program arguments")
    parser.add_argument("-u", "--useclang", dest='useclang', action='store_true', help='Use clang instead of llvm pass')
    parser.add_argument("-v", "--verbose", type=int, choices=[0, 1, 2, 3], default=2, help="Set output verbosity (0=error, 1=warning, 2=info, 3=low priority info)")
    stripped_argv = []
    remaining = []
    reached_args = False
    for arg in sys.argv[1:]:
        if arg == "-a" or arg == "--args":
            reached_args = True
            continue
        if reached_args:
            remaining.append(arg)
        else:
            stripped_argv.append(arg)
    args = parser.parse_args(stripped_argv)
    Verbose = args.verbose
    ProgramName = args.program
    Arguments = remaining
    use_clang = False
    if args.useclang:
        use_clang = True

    print("program:", ProgramName, "args:", Arguments, "useclang:", use_clang)

    kernel_names = extract_kernel_names(ProgramName)
    exception_flags = 0x7F

    conf = configparser.ConfigParser()
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
    conf.read(setup_file)

    for kernel in kernel_names:
        print("kernel name:", kernel)            
    print("total kernels: ", len(kernel_names))  

    kernel_seq = []
    saved_rips = []
    saved_locs = []
    injected_points = []
    kernel_disassemble = {}
    end_of_prog = False
    while not end_of_prog:
        LastParam = -1
        kernel_seq, saved_rips, saved_locs, kernel_disassemble, injected_points, end_of_prog = test_program(ProgramName, \
            kernel_names, kernel_seq, saved_rips, saved_locs, kernel_disassemble, injected_points)
        print("injected_points:", injected_points)
 
