include ../../common/make.config

CUDA_SDK_PATH := $(SDK_DIR)

# Determine the correct version of the cutil library
CUTIL_LIB = # -lcutil
ifeq ($(shell uname -m), x86_64)
     ifeq ($(shell if test -e $(SDK_DIR)/lib/libcutil_x86_64.a; then echo T; else echo F; fi), T)
        CUTIL_LIB = #-lcutil_x86_64
     endif
endif


all: euler3d_double #euler3d  pre_euler3d  pre_euler3d_double 

euler3d: euler3d.cu
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh $(INST_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o $(KERNEL_DIM) -g -O2 euler3d.cu -o euler3d

euler3d_double: euler3d_double.cu
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh $(INST_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -g -O3 euler3d_double.cu -o euler3d_double 

pre_euler3d: pre_euler3d.cu
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh $(INST_FLAGS) -O3 pre_euler3d.cu -o pre_euler3d 

pre_euler3d_double: pre_euler3d_double.cu
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh $(INST_FLAGS) -O3 pre_euler3d_double.cu -o pre_euler3d_double 


clean_base:
	rm -f euler3d euler3d_double pre_euler3d pre_euler3d_double *.linkinfo *.o *.s *.bc density density_energy momentum

clean: clean_base
	rm -f exp_flag.txt seq.txt inject_points.txt loc.txt