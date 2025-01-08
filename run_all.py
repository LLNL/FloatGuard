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
from pathlib import Path

Rodinia_Path = "benchmarks/rodinia_3.1/cuda"
PolyBench_Path = "benchmarks/PolyBench-ACC-0.1/CUDA"
NPB_Path = "benchmarks/NPB-GPU/CUDA"
Varity_Path = "benchmarks/cuda_examples/src"

Rodinia_Tests = ["backprop", "cfd", "gaussian", "heartwall", "hotspot", "hotspot3D", \
                "lavaMD", "lud", "myocyte", "nn", "nw", "particlefilter", "streamcluster"]

NPB_Tests = ["BT", "CG", "EP", "FT", "LU", "MG", "SP"]

PolyBench_Tests_datamining = ["correlation", "covariance"]
PolyBench_Tests_la_kernels = ["2mm", "3mm", "atax", "bicg", "doitgen", "gemm", "gemver", \
                              "gesummv", "mvt", "syr2k", "syrk"]
PolyBench_Tests_la_solvers = ["gramschmidt", "lu"]
PolyBench_Tests_stencils = ["adi", "convolution-2d", "convolution-3d", "fdtd-2d", "jacobi-1d-imper", "jacobi-2d-imper"]

all_paths = []

def test_path(full_path):
    if os.path.exists(full_path):
        all_paths.append(full_path)
    else:
        print("path", full_path, "do not exist")
        exit(0)

for i in range(1, 501):
    full_path = os.path.join(".", Varity_Path, "case_" + str(i))
    test_path(full_path)

for test in Rodinia_Tests:
    full_path = os.path.join(".", Rodinia_Path, test)
    test_path(full_path)

for test in NPB_Tests:
    full_path = os.path.join(".", NPB_Path, test)
    test_path(full_path)

for test in PolyBench_Tests_datamining:
    full_path = os.path.join(".", PolyBench_Path, "datamining", test)
    test_path(full_path)

for test in PolyBench_Tests_la_kernels:
    full_path = os.path.join(".", PolyBench_Path, "linear-algebra/kernels", test)
    test_path(full_path)

for test in PolyBench_Tests_la_solvers:
    full_path = os.path.join(".", PolyBench_Path, "linear-algebra/solvers", test)
    test_path(full_path)

for test in PolyBench_Tests_stencils:
    full_path = os.path.join(".", PolyBench_Path, "stencils", test)
    test_path(full_path)

for exp_path in all_paths:
    print("testing", exp_path)
    current_path = os.getcwd()
    os.chdir(exp_path)
    #os.system("make clean")
    #os.system("make cleanall")
    os.system("python3 -u ~/FloatGuard/gdb_script/time_measure.py")
    os.chdir(current_path)
    #input("continue...")