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

skipFunctionList = ["pow", "cbrt", "sqrtf64"]

PrintPrintf = False
PrintTrace = False
PrintCurInst = False

StepLine = True 

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

def test_program(program_name, kernel_names, orig_kernel_seq, saved_rips):
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
            return kernel_seq, saved_rips, True
        if "Arithmetic exception" in output:
            outlines = output.splitlines()
            startcopy = False
            print("----------------- EXCEPTION CAPTURED -----------------")
            for line in outlines:
                if "Arithmetic exception" in line:
                    startcopy = True
                if startcopy:
                    print(line.strip())
            trapsts = (int)(send(gdb, "p", "$trapsts&0x1ff").strip().split("=")[1].strip()) & exception_flags
            if trapsts & 0x01:
                print("trapsts: invalid")
            if trapsts & 0x02:
                print("trapsts: input denormal")                                
            if trapsts & 0x04:
                print("trapsts: divide by zero")
            if trapsts & 0x08:
                print("trapsts: overflow")
            if trapsts & 0x10:
                print("trapsts: underflow")
            if trapsts & 0x20:
                print("trapsts: inexact")
            if trapsts & 0x40:
                print("trapsts: integer divide by zero")
            bt_list = send(gdb, "bt", display=True).splitlines()
            print("----------------- EXCEPTION CAPTURE END -----------------")     
            idx = len(bt_list) - 1
            while idx >= 0:
                line = bt_list[idx].strip()
                m = re.search("#[0-9]+\s+(?:0x[0-9a-f]+\s+in\s)?([a-zA-Z0-9_]+)", line)
                if m:
                    exception_kernel_name = m.group(1)
                    break
                idx -= 1                       
            for idx in range(8):
                func_name = send(gdb, "p", "current_func[" + str(idx) + "]")
                if "__device_stub__" + exception_kernel_name + "(" in func_name:
                    rips_text = send(gdb, "p/x", "current_rips[" + str(idx) + "]").splitlines()[-1].strip().split()[-1]
                    saved_rips.append(rips_text)
                    break
            #while True:
            #    instr = input("(gdb) ")
            #    if instr.strip() == "skip":
            #        break
            #    else:
            #        send(gdb, instr, display=True)

            gdb.close()

            return kernel_seq, saved_rips, False
        else:
            print("other exceptions?") 
            print("-----------------")
            print("exception text:", output)
            print("-----------------")                                                                           
    output = send(gdb, "c")
    if "The program is not being run" in output:
        print("abort! 4")

    gdb.close()
    return kernel_seq, saved_rips, True

if __name__ == "__main__":
    if StepLine:
        PrintPrintf = False
        PrintTrace = False
        PrintCurInst = False
   
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interactive", dest='interactive', action='store_true', help='interactive mode')
    parser.add_argument("-s", "--skip", dest="skip", action='store_true', help="skip mode; only finds one exception in one kernel")
    parser.add_argument("-p", "--program", type=str, help="the program to be tested", required=True)
    parser.add_argument("-a", "--args", nargs='*', help="Program arguments")
    parser.add_argument("-c", "--config", type=str, help="config file")
    parser.add_argument("-v", "--verbose", type=int, choices=[0, 1, 2, 3], default=2, help="set output verbosity (0=error, 1=warning, 2=info, 3=low priority info)")
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
    Skip = args.skip

    print("program:", ProgramName, "args:", Arguments)

    kernel_names = extract_kernel_names(ProgramName)
    exception_flags = 0x7F

    if args.config:
        conf = configparser.ConfigParser()
        conf.read(args.config)
        if "DEFAULT" in conf:
            if "ExcludedFuncs" in conf["DEFAULT"]:
                funcs = conf['DEFAULT']['ExcludedFuncs'].split(";")
                for func in funcs:
                    kernel_names.remove(func)
            if "ExcludedExceptions" in conf["DEFAULT"]:
                excs = conf['DEFAULT']['ExcludedExceptions'].split(";")
                for exc in excs:
                    if exc == "invalid":
                        exception_flags &= ~(1 << 0)     
                    if exc == "inputDenormal":
                        exception_flags &= ~(1 << 1)
                    if exc == "float_div0":
                        exception_flags &= ~(1 << 2)
                    if exc == "overflow":
                        exception_flags &= ~(1 << 3)
                    if exc == "underflow":
                        exception_flags &= ~(1 << 4)
                    if exc == "inexact":
                        exception_flags &= ~(1 << 5)
                    if exc == "int_div0":
                        exception_flags &= ~(1 << 6)

    for kernel in kernel_names:
        print("kernel name:", kernel)            
    print("total kernels: ", len(kernel_names))  

    kernel_seq = []
    saved_rips = []
    end_of_prog = False
    while not end_of_prog:
        LastParam = -1
        kernel_seq, saved_rips, end_of_prog = test_program(ProgramName, kernel_names, kernel_seq, saved_rips)
        print("saved_rips:", saved_rips)
 