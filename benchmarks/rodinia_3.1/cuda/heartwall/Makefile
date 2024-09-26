include ../../common/make.config

ifdef OUTPUT
override OUTPUT = -DOUTPUT
endif

# link objects(binaries) together
heartwall: main.o ./AVI/avilib.o ./AVI/avimod.o 
	hipcc $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o main.o ./AVI/avilib.o ./AVI/avimod.o -lm -o heartwall

# compile main function file into object (binary)
main.o: main.cu kernel.cu define.c
	hipcc $(INST_FLAGS) ${HOME}/hipec/inst_pass/Inst/InstStub.o $(OUTPUT) $(KERNEL_DIM) main.cu -I./AVI -c -O3

./AVI/avilib.o ./AVI/avimod.o:
	cd AVI; make;

# delete all object files
clean:
	rm -f *.o AVI/*.o heartwall *.linkinfo
