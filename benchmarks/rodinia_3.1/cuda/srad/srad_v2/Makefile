include ../../../common/make.config

CC := hipcc

SRC = srad.cu

EXE = srad

release: $(SRC)
	$(CC) $(INST_FLAGS) $(KERNEL_DIM) $(SRC) -o $(EXE)

enum: $(SRC)
	$(CC) $(INST_FLAGS) $(KERNEL_DIM) -deviceemu $(SRC) -o $(EXE)

debug: $(SRC)
	$(CC) $(INST_FLAGS) $(KERNEL_DIM) -g $(SRC) -o $(EXE)

debugenum: $(SRC)
	$(CC) $(INST_FLAGS) $(KERNEL_DIM) -g -deviceemu $(SRC) -o $(EXE) 

clean: $(SRC)
	rm -f $(EXE) $(EXE).linkinfo result.txt
