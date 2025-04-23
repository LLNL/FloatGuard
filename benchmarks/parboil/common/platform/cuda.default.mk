# (c) 2007 The Board of Trustees of the University of Illinois.

# Cuda-related definitions common to all benchmarks

########################################
# Variables
########################################

# c.default is the base along with CUDA configuration in this setting
include $(PARBOIL_ROOT)/common/platform/c.default.mk

# Paths
CUDAHOME=

# Programs
CUDACC=${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh
CUDALINK=${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

# Flags
PLATFORM_CUDACFLAGS=-O3 -g
PLATFORM_CUDALDFLAGS=-lm -lpthread -fgpu-rdc --hip-link


