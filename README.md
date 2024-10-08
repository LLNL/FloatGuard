# FloatGuard - HIP Exception Capture

## Overview

FloatGuard is a tool that captures floating-point exceptions in your AMD HIP kernels.
It is as of now the only publicly available tool that detects and captures
runtime floating-point exception information in AMD HIP programs running on AMD
GPUs. FloatGuard does this by injecting code that controls exception capture
registers, and a novel algorithm that adapts to the hardware properties of AMD
GPUs, in order to detect as many source code locations that cause floating-point
exceptions as possible. 

## Build and Run

### Prerequisites

1. Linux system. We have tested on Ubuntu 22.04.
2. AMD GPU with ROCm installed. Tested on ROCm 6.1.2 with AMD Clang 17.0.0.
When you run `rocminfo` and `hipcc -v` in command line, it shows system, GPU and
compiler attributes normally. Follow
https://rocm.docs.amd.com/projects/install-on-linux/en/latest/ for more
information on how to install AMD ROCm. Please make sure there is only AMD Clang
present in your system, as it would interfere with other copies of Clang.

### Build

1. Clone this GitHub repository to a local directory of your choice.

```
git clone https://github.com/LLNL/FloatGuard [FloatGuard directory]
```

2. Run `build_single_plugin.sh` in the code repository directory to build the
library, Clang plugin and LLVM pass used in the tool.

### How to Use FloatGuard to capture floating-point exceptions

FloatGuard supports using Clang plugin or LLVM pass to inject code into the target
program to capture floating-point exceptions. The following are instructions
for both methods, using a sample program found in `samples/div0` as example:

#### Clang plugin

1. Create a configuration in the build script of the target program that appends
the following command line options to the C++ compilation command of each source file.

```
-emit-llvm -Xclang -load -Xclang [FloatGuard directory]/clang-examples/FloatGuard-plugin/FloatGuard-plugin.so -Xclang -plugin -Xclang inject-fp-exception 
```

You can check out how this is implemented in the sample program in `Makefile`
with `INJECT_CODE_CLANG` flag set to 1. For CMake codebase, you can append these
command line options to `CMAKE_CXX_FLAGS`.

2. Next, add the following command line options to the regular compilation
options of each source file in the build script, so that the header files for
FloatGuard is included. You can check out how this is implemented in the sample
program in `Makefile` as well. for CMake codebase, you can append these command
line options to `CMAKE_CXX_FLAGS`.

```
-include [FloatGuard directory]/inst_pass/Inst/InstStub.h 
```

3. Also, add the following object file name to the link command of the targeted
program, so that the code library is linked. You can also find it in the
`Makefile` in the sample program. In CMake codebase, you can append it to
`CMAKE_EXE_LINKER_FLAGS`, or `CMAKE_SHARED_LINKER_FLAGS` if you are building a
shared library.

```
${HOME}/FloatGuard/inst_pass/Inst/InstStub.o
```

4. Run the build script of the target program with the configuration you just
created. In the sample program, this is done by calling `make
INJECT_CODE_CLANG=1`. The Clang plugin will inject calls to control
floating-point exception handling to the source code of the target program.
When this step is finished, there will be a link error at the end, which can be
ignored.

5. Build the targeted program normally. In the sample program, this is done by
simply calling `make`.

6. Once you have a []

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

Run the following command in the directory of the benchmark program:

```
python3 ~/FloatGuard/gdb_test/time_measure.py
```

The benchmarks are all inside the `benchmarks` folder, which was downloaded when
`setup.sh` is run. All directories that can run the Python command has a
`setup.ini` file, which contains instructions for FloatGuard.

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
