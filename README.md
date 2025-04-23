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

1. Linux system. We have tested on Ubuntu 22.04 and TOSS 4.
2. Python (>= 3.9) installed.
3. AMD GPU with ROCm installed. Tested on ROCm 6.1.2 with AMD Clang 17.0.0.
Follow https://rocm.docs.amd.com/projects/install-on-linux/en/latest/ for more
information on how to install AMD ROCm. Specifically, make sure both `rocm` and 
`rocm-llvm-dev` packages are installed.

### Deploy FloatGuard

Clone this GitHub repository with the following command.

```
git clone https://github.com/LLNL/FloatGuard [FloatGuard Directory]
```

## Running FloatGuard on a benchmark program

We provide 41 benchmark programs besides the sample programs, which can 
be used to validate your FloatGuard installation.

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
then run the following command.

```
python3 [FloatGuard Directory]/gdb_script/time_measure.py
```

Log files containing details on the floating-point exceptions found are
outputted as `[experiment]_output.txt` file in the FloatGuard code repo directory.
Also `result.csv` updates the running time statistics and the number of
exceptions found.

## How to Use FloatGuard to capture floating-point exceptions

The following are instructions for setting up the AMD HIP code project of your own to use FloatGuard.

1. Replace the compiler in your code project with our wrapper. For example, if your
code project uses the HIPCC macro in a Makefile to indicate compiler command, you should replace
it with this:

```
HIPCC = ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh
```

2. If your code project has multiple source files, but you use a single compiler command
to compile and link the sources, please separate the compile and link commands into two.
For example:

```
${HIPCC} ${HIPFLAGS} -c main.cpp -o main.o
${HIPCC} ${HIPFLAGS} -c other.cpp -o other.o
${HIPCC} ${LINKFLAGS} main.o other.o -o main
```

3. Enter the root directory of your project, then call the `time_measure.py` script to run 
the FloatGuard tool. After it is done,

```
[FloatGuard Directory]/gdb_script/time_measure.py
```

Log files containing details on the floating-point exceptions found are
outputted as `[code project directory name]_output.txt` file in the FloatGuard code repo directory.
Also `result.csv` updates the running time statistics and the number of
exceptions found.

### Samples for make and CMake projects

We provide two example projects, `samples/div0` and `samples/div0_cmake`, for developers
to try out and learn what is required for your own HIP code to work with FloatGuard.
You can refer to `samples/div0/Makefile` and `samples/div0_cmake/CMakeLists.txt` for examples
of the steps described in previous sections. The following are instructions on how to
capture floating-point exceptions for these sample programs, starting from each diretory:

## Try out our demo in a Docker container 

If you do not want to install additional software on your system or just want to
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
make
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
