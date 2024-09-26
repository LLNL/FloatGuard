include ../../common/make.config

CC := hipcc

SRC = needle.cu

EXE = needle

release: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o ${KERNEL_DIM} $(SRC) -o $(EXE)

enum: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o ${KERNEL_DIM} -deviceemu $(SRC) -o $(EXE)
	
debug: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o ${KERNEL_DIM} -g $(SRC) -o $(EXE)

debugenum: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o${KERNEL_DIM} -g -deviceemu $(SRC) -o $(EXE)

clean: $(SRC)
	rm -f $(EXE) $(EXE).linkinfo result.txt
