include ../../../common/make.config

CC = gcc
NVCC = hipcc

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
	$(NVCC) $(KERNEL_DIM) $(NVCCFLAGS) $(DEFS) -o $@ -c $<

%.o:	%.cu 
	$(NVCC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(KERNEL_DIM) $(NVCCFLAGS) $(DEFS) -o $@ -c $< 


$(EXECUTABLE) : $(OBJS)
	$(NVCC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(NVCCFLAGS) -o $@  $?

clean:
	rm -f $(EXECUTABLE) $(OBJS) *.linkinfo
