include ../../common/make.config

ifdef OUTPUT
override OUTPUT = -DOUTPUT
endif

# link objects(binaries) together
heartwall: main.o ./AVI/avilib.o ./AVI/avimod.o 
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh $(INST_FLAGS)  main.o ./AVI/avilib.o ./AVI/avimod.o -lm -o heartwall

# compile main function file into object (binary)
main.o: main.cu kernel.cu define.c
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh $(INST_FLAGS)  $(OUTPUT) $(KERNEL_DIM) main.cu -I./AVI -c -O3

./AVI/avilib.o ./AVI/avimod.o:
	cd AVI; make;

# delete all object files
clean_base:
	rm -f *.s *.o AVI/*.o heartwall *.linkinfo

clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/