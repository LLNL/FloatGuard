include ../../../common/make.config

CC = gcc
NVCC = ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

DEFS += \
		-DGPU_TIMER \
		$(SPACE)

NVCCFLAGS += -I../common \
			 -O3 \
			 -ffast-math \
			 -lm \
			 $(SPACE)

CFLAGS += -I../common \
					-I/usr/include/cuda \
		  -O3 \
		  -Wall \
		  $(SPACE)

# Add source files here
EXECUTABLE  := lud_cuda
# Cuda source files (compiled with cudacc)
CUFILES     := lud_kernel.cu
# C/C++ source files (compiled with gcc / c++)
CCFILES     := lud.c lud_cuda.c ../common/common.c

OBJS = ../common/common.o lud.o lud_kernel.o

.PHONY: all clean 
all : $(EXECUTABLE)

.c.o : 
	$(CC) $(KERNEL_DIM) $(NVCCFLAGS) $(DEFS) -o $@ -c $<

%.o:	%.cu 
	$(NVCC) $(INST_FLAGS)  $(KERNEL_DIM) $(NVCCFLAGS) $(DEFS) -o $@ -c $< 


$(EXECUTABLE) : $(OBJS)
	$(NVCC) $(INST_FLAGS)  $(NVCCFLAGS) -o $@  $?

clean_base:
	-rm -f *.s *.o $(EXECUTABLE) $(OBJS) *.linkinfo

clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/