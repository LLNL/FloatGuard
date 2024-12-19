include ../../common/make.config

NVCC = ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

TARGET_G = sc_gpu


# make dbg=1 tells nvcc to add debugging symbols to the binary
ifeq ($(dbg),1)
	NVCC_FLAGS += -g -O0
else
	NVCC_FLAGS += -O3
endif

# make emu=1 compiles the CUDA kernels for emulation
ifeq ($(emu),1)
	NVCC_FLAGS += -deviceemu
endif


$(TARGET_G): streamcluster_cuda_cpu.cpp streamcluster_cuda.cu streamcluster_header.cu
	$(NVCC) $(NVCC_FLAGS) $(INST_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o streamcluster_cuda_cpu.cpp streamcluster_cuda.cu streamcluster_header.cu -o $(TARGET_G)
	

clean:
	rm -f *.o *~ *.txt $(TARGET_G) *.linkinfo
	
