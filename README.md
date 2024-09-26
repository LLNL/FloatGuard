# HIPEC - HIP Exception Capture (tentative)

HIPEC is a tool that captures floating-point exceptions in your AMD HIP kernels.

Usage:

1. Clone this repository to your home directory.

```
cd ~
git clone https://github.com/doloresmiao/hip_llvm hipec/
```

2. Run this script to compile Clang plugin and LLVM pass used by HIPEC.

```
cd ~/hipec
./build_single_plugin.sh
```

3. Add calls to either Clang plugin or LLVM pass in your build scripts.

4. Add a `setup.ini` file in your code repo, which contains instructions for HIPEC.
An example can be found below.

```
[DEFAULT]
compile = make
run = ./sc_gpu 10 20 256 65536 65536 1000 none output.txt 1
use_clang_plugin = false
clang_convert = make INJECT_CODE_CLANG=1
llvm_pass = make INJECT_CODE_LLVM=1
clean = make clean
```