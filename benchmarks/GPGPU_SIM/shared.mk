# compiler
CC = gcc
CC_FLAGS = -Wall
#CC_FLAGS = -O3 

# CUDA compiler
NVCC = ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh
#NVCC_FLAGS = -arch=sm_70  #-O3 
NVCC_FLAGS = -g -O3 -I. -I..
# Link

LINK_FLAG = -fgpu-rdc --hip-link #