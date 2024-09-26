include ../../common/make.config

CC := hipcc

SRC = 3D.cu

EXE = 3D 

OUTPUT = *.out

FLAGS = -g #-arch sm_20 --ptxas-options=-v
release: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(KERNEL_DIM) $(FLAGS) $(SRC) -o $(EXE)

enum: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(KERNEL_DIM) $(FLAGS) -deviceemu $(SRC) -o $(EXE)

debug: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(KERNEL_DIM) $(FLAGS) -g $(SRC) -o $(EXE)

debugenum: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(KERNEL_DIM) $(FLAGS) -g -deviceemu $(SRC) -o $(EXE)

clean: $(SRC)
	rm -f $(EXE) $(EXE).linkinfo $(OUTPUT) 
