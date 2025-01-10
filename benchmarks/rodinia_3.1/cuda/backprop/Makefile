include ../../common/make.config

# C compiler
CC = gcc
CC_FLAGS = -g  -O2

# CUDA compiler
NVCC = ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh
NVCC_FLAGS = $(INST_FLAGS)

# 'make dbg=1' enables NVCC debugging
ifeq ($(dbg),1)
	NVCC_FLAGS += -g -O0
else
	NVCC_FLAGS += -O2
endif

# 'make emu=1' compiles the CUDA kernels for emulation
ifeq ($(emu),1)
	NVCC_FLAGS += -deviceemu
endif

backprop: backprop.o facetrain.o imagenet.o backprop_cuda.o 
	$(NVCC) $(CC_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o backprop.o facetrain.o imagenet.o backprop_cuda.o -o backprop -lm

%.o: %.[ch]
	$(CC) $(CC_FLAGS) $< -c

facetrain.o: facetrain.c backprop.h
	$(CC) $(CC_FLAGS) facetrain.c -c
	
backprop.o: backprop.c backprop.h
	$(CC) $(CC_FLAGS) backprop.c -c

backprop_cuda.o: backprop_cuda.cu backprop.h
	$(NVCC) $(NVCC_FLAGS) -c backprop_cuda.cu

imagenet.o: imagenet.c backprop.h
	$(CC) $(CC_FLAGS) imagenet.c -c


clean_base:
	rm -f *.o *.s *~ backprop backprop_cuda.linkinfo

clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/