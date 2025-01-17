include ../../common/make.config

CC := ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

SRC = 3D.cu

EXE = 3D 

OUTPUT = *.out

FLAGS = -g #-arch sm_20 --ptxas-options=-v
release: $(SRC)
	$(CC) $(INST_FLAGS)  $(KERNEL_DIM) $(FLAGS) $(SRC) -o $(EXE)

enum: $(SRC)
	$(CC) $(INST_FLAGS)  $(KERNEL_DIM) $(FLAGS) -deviceemu $(SRC) -o $(EXE)

debug: $(SRC)
	$(CC) $(INST_FLAGS)  $(KERNEL_DIM) $(FLAGS) -g $(SRC) -o $(EXE)

debugenum: $(SRC)
	$(CC) $(INST_FLAGS)  $(KERNEL_DIM) $(FLAGS) -g -deviceemu $(SRC) -o $(EXE)

clean_base: $(SRC)
	-rm -f *.s $(EXE) $(EXE).linkinfo $(OUTPUT) 

clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/