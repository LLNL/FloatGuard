# HIPEC - HIP Exception Capture

## Overview

HIPEC is a tool that captures floating-point exceptions in your AMD HIP kernels.
It is as of now the only publicly available tool that detects and captures
runtime floating-point exception information in AMD HIP programs running on AMD
GPUs. HIPEC does this by injecting code that controls exception capture
registers, and a novel algorithm that adapts to the hardware properties of AMD
GPUs, in order to detect as many source code locations that cause floating-point
exceptions as possible. 

## Installation, Setup, and Running Example Programs

### Prerequisites

1. Linux system. We have tested on Ubuntu 22.04.
2. AMD GPU with ROCm installed. When you run `rocminfo` in command line, it
shows system and GPU attributes normally. Follow
https://rocm.docs.amd.com/projects/install-on-linux/en/latest/ for more
information on how to install AMD ROCm.
3. 10 GiB free disk space recommended.
4. Docker is installed on your system, and it is verified that you can call
   `docker pull` with non-root user without using `sudo`.
5. Clone this GitHub repository to a local directory of your choice.

```
git clone https://github.com/LLNL/HIPEC [HIPEC directory]
```

### Setup Docker container with code repository

We have two options to set up the reproduction environment.

#### Option 1: pull and run Docker container from DockerHub

In the Linux terminal, execute the following commands to pull the Docker
container and run it. After entering the root user bash prompt inside the Docker
container. The shell script will detect if you already have the container. If
not, it will run it; otherwise, it simply resumes running.

```
cd [HIPEC directory]
./run_docker.sh
```

#### Option 2: build your own Docker container on local machine

Build the Docker image using the Dockerfile inside the code repository, then run
the Docker container. Please note that the RAM + swap area of your local PC must
be no less than 32GiB in order to finish building without errors. It takes
several hours to finish building the docker image.

```
cd [HIPEC directory]
docker build . -t ucdavisplse/hipec:latest
./run_docker.sh
```

### Setup environment and build tools

Run the initial setup script (`setup.sh`) to install third-party software,
download benchmark programs, compile Clang plugin, and compile LLVM pass
required by HIPEC to run.

```
cd root/hipec
source setup.sh
./build_single_plugin.sh
```

### Run an individual experiment

Run the following command in the directory of the benchmark program:

```
python3 ~/hipec/gdb_test/time_measure.py
```

The benchmarks are all inside the `benchmarks` folder, which was downloaded when
`setup.sh` is run. All directories that can run the Python command has a
`setup.ini` file, which contains instructions for HIPEC.

Log files containing details on the floating-point exceptions found are
outputted as `[experiment]_output.txt` file in the HIPEC code repo directory.
Also `result.csv` updates the running time statistics and the number of
exceptions found.

### Run all experiments

Run the following command in the code repository directory:

```
python3 run_all.py
```

## License

HIPEC is distributed under the terms of the MIT License.

See LICENSE and NOTICE for details.

LLNL-CODE-xxxxxx
