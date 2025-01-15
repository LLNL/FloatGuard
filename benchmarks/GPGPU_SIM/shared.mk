# CUDA toolkit installation path
CUDA_DIR = /usr/local/cuda

# CUDA SDK installation path
SDK_DIR = $(HOME)/NVIDIA_GPU_Computing_SDK/

# CUDA toolkit libraries
LIB_DIR = $(CUDA_DIR)/lib64

# compiler
CC = gcc
CC_FLAGS = -Wall
#CC_FLAGS = -O3 

# CUDA compiler
NVCC = $(CUDA_DIR)/bin/nvcc --generate-line-info
#NVCC_FLAGS = -arch=sm_70  #-O3 
NVCC_FLAGS = -arch=sm_70 -O3 #-use_fast_math
# Link
NVCC_INCLUDE = -I. -I.. -I$(CUDA_DIR)/include #-I$(SDK_DIR)/C/common/inc -I../common/inc/ -I$(SDK_DIR)/shared/inc 
NVCC_LIB = -lcuda -lcudart #-lcutil_x86_64 -lcuda  
NVCC_LIB_PATH = -L. -L$(LIB_DIR)/ #-L$(SDK_DIR)/C/lib -L$(LIB_DIR)/ -L$(SDK_DIR)/shared/lib

LINK_FLAG = $(NVCC_INCLUDE) $(NVCC_LIB_PATH) $(NVCC_LIB) -lstdc++ -lm
