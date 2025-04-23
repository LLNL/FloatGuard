include ../../common/make.config

CC := ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

SRC = hotspot.cu

EXE = hotspot

release: $(SRC)
	$(CC) $(INST_FLAGS)  $(KERNEL_DIM) $(SRC) -o $(EXE)

enum: $(SRC)
	$(CC) $(INST_FLAGS)  $(KERNEL_DIM) -deviceemu $(SRC) -o $(EXE)

debug: $(SRC)
	$(CC) $(INST_FLAGS)  $(KERNEL_DIM) -g $(SRC) -o $(EXE)

debugenum: $(SRC)
	$(CC) $(INST_FLAGS)  $(KERNEL_DIM) -g -deviceemu $(SRC) -o $(EXE)

clean_base: $(SRC)
	-rm -f *.s $(EXE) $(EXE).linkinfo result.txt

clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/