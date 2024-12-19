#makefile

include ../../common/make.config

CC := ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

all: naive float

naive: ex_particle_CUDA_naive_seq.cu
	$(CC)  -g -lm -O3 -ffast-math $(INST_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o ex_particle_CUDA_naive_seq.cu -o particlefilter_naive
	
float: ex_particle_CUDA_float_seq.cu
	$(CC) -g -lm -O3 -ffast-math $(INST_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o ex_particle_CUDA_float_seq.cu -o particlefilter_float

clean:
	rm particlefilter_naive particlefilter_float
