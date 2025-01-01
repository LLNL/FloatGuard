include ../../common/make.config

LOCAL_CC = gcc -g -O3 -Wall
CC := ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

all : nn hurricane_gen

clean_base:
	-rm -rf *.s *.o nn hurricane_gen

clean: clean_base
	rm -f exp_flag.txt seq.txt inject_points.txt loc.txt

nn : nn_cuda.cu
	$(CC) -c $(INST_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o nn_cuda.cu
	$(CC) $(INST_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -o nn nn_cuda.o

hurricane_gen : hurricane_gen.c
	$(LOCAL_CC) -o $@ $< -lm

#data :
#	mkdir data
#	./gen_dataset.sh
