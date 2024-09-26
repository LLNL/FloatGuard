include ../../common/make.config

CUDA_SDK_PATH := $(SDK_DIR)

# Determine the correct version of the cutil library
CUTIL_LIB = # -lcutil
ifeq ($(shell uname -m), x86_64)
     ifeq ($(shell if test -e $(SDK_DIR)/lib/libcutil_x86_64.a; then echo T; else echo F; fi), T)
        CUTIL_LIB = #-lcutil_x86_64
     endif
endif


all: euler3d #euler3d_double  pre_euler3d  pre_euler3d_double 

euler3d: euler3d.cu
	hipcc $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(KERNEL_DIM) -g -O2 euler3d.cu -o euler3d

euler3d_double: euler3d_double.cu
	hipcc $(INST_FLAGS) -O3 euler3d_double.cu -o euler3d_double 


pre_euler3d: pre_euler3d.cu
	hipcc $(INST_FLAGS) -O3 pre_euler3d.cu -o pre_euler3d 

pre_euler3d_double: pre_euler3d_double.cu
	hipcc $(INST_FLAGS) -O3 pre_euler3d_double.cu -o pre_euler3d_double 


clean:
	rm -f euler3d euler3d_double pre_euler3d pre_euler3d_double *.linkinfo *.o *.bc density density_energy momentum
