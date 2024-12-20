#!/bin/bash

# Check if the script is running as root
if [ $EUID -ne 0 ]; then
    sudo apt update && sudo apt install dos2unix unzip
    exit 1
else
    apt update && apt install dos2unix unzip
fi

# NPB-GPU
cd benchmarks
git clone https://github.com/GMAP/NPB-GPU
cd NPB-GPU
git checkout f65e28b349bd08594bf94fa22c090c4d70e90ccb
git apply ../NPB-GPU-patch.txt
cd ..

# PolyBench-ACC
wget https://github.com/cavazos-lab/PolyBench-ACC/archive/refs/tags/v0.1.zip
unzip v0.1.zip
rm v0.1.zip
cd PolyBench-ACC-0.1
rm -r HMPP/ OpenACC/ OpenCL/ OpenMP/
cd ..
patch -p0 < PolyBench-patch.txt

# Rodinia

sh setup_rodinia.sh

cd ..