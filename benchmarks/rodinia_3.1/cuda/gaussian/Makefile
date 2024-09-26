include ../../common/make.config

CC := hipcc

INCLUDE := 

SRC = gaussian.cu
EXE = gaussian

release: $(SRC)
	$(CC) $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(KERNEL_DIM) $(SRC) -o $(EXE)

clean:
	rm gaussian
