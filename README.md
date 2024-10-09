# FloatGuard - HIP Exception Capture

## Overview

FloatGuard is a tool that captures floating-point exceptions in your AMD HIP kernels.
It is as of now the only publicly available tool that detects and captures
runtime floating-point exception information in AMD HIP programs running on AMD
GPUs. FloatGuard does this by injecting code that controls exception capture
registers, and a novel algorithm that adapts to the hardware properties of AMD
GPUs, in order to detect as many source code locations that cause floating-point
exceptions as possible. 

## Build FloatGuard

### Prerequisites

1. Linux system. We have tested on Ubuntu 22.04.
2. AMD GPU with ROCm installed. Tested on ROCm 6.1.2 with AMD Clang 17.0.0.
Follow https://rocm.docs.amd.com/projects/install-on-linux/en/latest/ for more
information on how to install AMD ROCm. Specifically, make sure both `rocm` and 
`rocm-llvm-dev` packages are installed.

### Build

1. Clone this GitHub repository to a local directory of your choice.

```
git clone https://github.com/LLNL/FloatGuard $HOME/FloatGuard
```

2. Run `build_single_plugin.sh` in the code repository directory to build the
library, Clang plugin and LLVM pass used in the tool.

## How to Use FloatGuard to capture floating-point exceptions

FloatGuard supports using Clang plugin or LLVM pass to inject code into the
target program to capture floating-point exceptions. The following are
instructions for both methods.

### Prerequisites for both methods

1. Create a RANDINT macro in your build system with the following shell command,
which is required for FloatGuard to differentiate between different source files.
The following is example code for Makefiles:

```
RANDINT = $(shell python3 -c 'from random import randint; print(randint(1000000000, 9999999999));')
```

2. Add the following command line options to the regular compilation
options of each source file in the build script,

```
-include ${HOME}/FloatGuard/inst_pass/Inst/InstStub.h 
```

### Clang plugin

1. Create a configuration in the build script of the target program that appends
the following command line options to the C++ compilation command of each source file.

```
-emit-llvm -Xclang -load -Xclang [FloatGuard directory]/clang-examples/FloatGuard-plugin/FloatGuard-plugin.so -Xclang -plugin -Xclang inject-fp-exception 
```

3. Also, add the following object file name to the link command of the targeted
program, so that the code library is linked.

```
${HOME}/FloatGuard/inst_pass/Inst/InstStub.o
```

4. Run the build script of the target program with the configuration you just
created.

5. Build the targeted program normally. In the sample program, this is done by
simply calling `make`.

6. Run the following command to capture floating-point exceptions on the injected
target program.

```
$HOME/FloatGuard/gdb_script/exception_capture_rerun.py -p [program binary] -a [arguments]
```

### LLVM pass

1. Create a configuration in the build script of the target program that appends
the following command line options to the C++ compilation command of each source file.

```
-fpass-plugin=${HOME}/FloatGuard/inst_pass/libInstPass.so
```

2. Run the build script of the target program with the configuration you just
created, so that executable binary is created with 

3. Run the following command to capture floating-point exceptions on the injected
target program.

```
$HOME/FloatGuard/gdb_script/exception_capture_rerun.py -p [program binary] -a [arguments]
```

### Samples for make and CMake projects

We provide two example projects, `samples/div0` and `samples/div0_cmake`, for developers
to better understand the setup required for your own HIP code to work with FloatGuard.
You can refer to `samples/div0/Makefile` and `samples/div0_cmake/CMakeLists.txt` for examples
of the steps described in previous sections. The following are instructions on how to
capture floating-point exceptions for these sample programs, starting from each diretory:

#### samples/div0

Clang plugin:

```
make INJECT_CODE_CLANG=1
make clean
make
$HOME/FloatGuard/gdb_script/exception_capture_rerun.py -p div0
```

LLVM pass:
```
make INJECT_CODE_LLVM=1
$HOME/FloatGuard/gdb_script/exception_capture_rerun.py -p div0
```

#### samples/div0_cmake

Clang plugin:

```
mkdir build
cd build
cmake -DINJECT_CODE_CLANG=1 ..
make
rm -r *
cmake ..
make
$HOME/FloatGuard/gdb_script/exception_capture_rerun.py -p div0
```

LLVM pass:

```
mkdir build
cd build
cmake -DINJECT_CODE_LLVM=1 ..
make
$HOME/FloatGuard/gdb_script/exception_capture_rerun.py -p div0
```

## Running FloatGuard on a benchmark program

We provide 41 benchmark programs besides the sample programs, which can 
be used to validate your FloatGuard installation and compare the results
to our findings in our publication.

First, run `setup.sh` to download and unpack these benchmark programs.
The directories of these programs are listed below:

```
benchmarks/rodinia_3.1/cuda/backprop
benchmarks/rodinia_3.1/cuda/cfd
benchmarks/rodinia_3.1/cuda/gaussian
benchmarks/rodinia_3.1/cuda/heartwall
benchmarks/rodinia_3.1/cuda/hotspot
benchmarks/rodinia_3.1/cuda/hotspot3D
benchmarks/rodinia_3.1/cuda/lavaMD
benchmarks/rodinia_3.1/cuda/lud
benchmarks/rodinia_3.1/cuda/myocyte
benchmarks/rodinia_3.1/cuda/nn
benchmarks/rodinia_3.1/cuda/nw
benchmarks/rodinia_3.1/cuda/particlefilter
benchmarks/rodinia_3.1/cuda/streamcluster
benchmarks/NPB-GPU/CUDA/BT
benchmarks/NPB-GPU/CUDA/CG
benchmarks/NPB-GPU/CUDA/EP
benchmarks/NPB-GPU/CUDA/FT
benchmarks/NPB-GPU/CUDA/LU
benchmarks/NPB-GPU/CUDA/MG
benchmarks/NPB-GPU/CUDA/SP
benchmarks/PolyBench-ACC-0.1/CUDA/datamining/correlation
benchmarks/PolyBench-ACC-0.1/CUDA/datamining/covariance
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/2mm
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/3mm
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/atax
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/bicg
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/doitgen
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/gemm
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/gemver
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/gesummv
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/mvt
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/syr2k
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/kernels/syrk
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/solvers/gramschmidt
benchmarks/PolyBench-ACC-0.1/CUDA/linear-algebra/solvers/lu
benchmarks/PolyBench-ACC-0.1/CUDA/stencils/adi
benchmarks/PolyBench-ACC-0.1/CUDA/stencils/convolution-2d
benchmarks/PolyBench-ACC-0.1/CUDA/stencils/convolution-3d
benchmarks/PolyBench-ACC-0.1/CUDA/stencils/fdtd-2d
benchmarks/PolyBench-ACC-0.1/CUDA/stencils/jacobi-1d-imper
benchmarks/PolyBench-ACC-0.1/CUDA/stencils/jacobi-2d-imper
```

To run a benchmark program, change current directory to one of them,
then run the following command. The `time_measure.py` script automatically
runs the command lines as described in the prevous section for these benchmark
programs, 

```
python3 $HOME/FloatGuard/gdb_script/time_measure.py
```

Log files containing details on the floating-point exceptions found are
outputted as `[experiment]_output.txt` file in the FloatGuard code repo directory.
Also `result.csv` updates the running time statistics and the number of
exceptions found.

## Try out our demo in a Docker container 

If you do not want to install software on your system or just want to
check out how the tool works, you can try out our demo in a Docker container.

### Prerequisites

1. Linux system. We have tested on Ubuntu 22.04.
2. AMD GPU with kernel driver (`amdgpu-dkms`) installed. When you run `rocm-smi` in command line, it
shows system and GPU attributes normally. Follow
https://rocm.docs.amd.com/projects/install-on-linux/en/latest/ for more
information on how to install AMD ROCm.
3. 10 GiB free disk space recommended.
4. Docker is installed on your system, and it is verified that you can call
   `docker pull` with non-root user without using `sudo`.
5. Clone this GitHub repository to a local directory of your choice.

```
git clone https://github.com/LLNL/FloatGuard [FloatGuard directory]
```

### Set the AMD GPU you want to use

In `[FloatGuard directory]/run_docker.sh`, please follow the instructions from 
https://rocm.docs.amd.com/projects/install-on-linux/en/latest/how-to/docker.html#restricting-gpu-access
and change the text `--device=/dev/dri` to the GPU device file you want to use.
For example, if your AMD GPU is number 0, please use `--device /dev/dri/renderD128`.

### Setup Docker container with code repository

We have two options to set up the reproduction environment.

#### Option 1: pull and run Docker container from DockerHub

In the Linux terminal, execute the following commands to pull the Docker
container and run it. After entering the root user bash prompt inside the Docker
container. The shell script will detect if you already have the container. If
not, it will run it; otherwise, it simply resumes running.

```
cd [FloatGuard directory]
./run_docker.sh
```

#### Option 2: build your own Docker container on local machine

Build the Docker image using the Dockerfile inside the code repository, then run
the Docker container. Please note that the RAM + swap area of your local PC must
be no less than 32GiB in order to finish building without errors. It takes
several hours to finish building the docker image.

```
cd [FloatGuard directory]
docker build . -t ucdavisplse/FloatGuard:latest
./run_docker.sh
```

### Setup environment and build tools

Run the initial setup script (`setup.sh`) to install third-party software,
download benchmark programs, compile Clang plugin, and compile LLVM pass
required by FloatGuard to run.

```
cd root/FloatGuard
source setup.sh
./build_single_plugin.sh
```

### Run an individual experiment

Run the following command in the directory of the benchmark program. The
directory for these programs are listed in a previous section.

```
python3 ~/FloatGuard/gdb_test/time_measure.py
```

Log files containing details on the floating-point exceptions found are
outputted as `[experiment]_output.txt` file in the FloatGuard code repo directory.
Also `result.csv` updates the running time statistics and the number of
exceptions found.

### Run all experiments

Run the following command in the code repository directory:

```
python3 run_all.py
```

## License

FloatGuard is distributed under the terms of the MIT License.

See LICENSE and NOTICE for details.

LLNL-CODE-xxxxxx
