include ../../common/make.config

CC := ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

INCLUDE := 

SRC = gaussian.cu
EXE = gaussian

release: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o $(KERNEL_DIM) $(SRC) -o $(EXE)

clean_base:
	-rm gaussian *.s *.o

clean: clean_base
	rm -f exp_flag.txt seq.txt inject_points.txt loc.txt