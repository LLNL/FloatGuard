include ../../common/make.config

LOCAL_CC = gcc -g -O3 -Wall
CC := ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

all : nn hurricane_gen

clean_base:
	-rm -rf *.s *.o nn hurricane_gen

clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/

nn : nn_cuda.cu
	$(CC) -c $(INST_FLAGS)  nn_cuda.cu
	$(CC) $(INST_FLAGS)  -o nn nn_cuda.o

hurricane_gen : hurricane_gen.c
	$(LOCAL_CC) -o $@ $< -lm

#data :
#	mkdir data
#	./gen_dataset.sh
