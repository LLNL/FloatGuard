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


$(TARGET_G):
	$(NVCC) -c $(NVCC_FLAGS) $(INST_FLAGS) streamcluster_cuda_cpu.cpp 
	$(NVCC) -c $(NVCC_FLAGS) $(INST_FLAGS) streamcluster_cuda.cu 
	$(NVCC) -c $(NVCC_FLAGS) $(INST_FLAGS) streamcluster_header.cu 
	$(NVCC) $(NVCC_FLAGS) $(INST_FLAGS) streamcluster_cuda_cpu.o streamcluster_cuda.o streamcluster_header.o ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -o $(TARGET_G)
	

clean_base:
	-rm -f *.o *.s *~ *.txt $(TARGET_G) *.linkinfo
	
clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/