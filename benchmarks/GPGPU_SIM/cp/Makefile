include ../shared.mk

cp: cuenergy_pre8_coalesce.cu main.cu parboil.c
	$(NVCC) $(NVCC_FLAGS) -c cuenergy_pre8_coalesce.cu
	$(NVCC) $(NVCC_FLAGS) -c main.cu
	$(CC) $(CC_FLAGS) -c parboil.c
	$(NVCC) $(NVCC_FLAGS) cuenergy_pre8_coalesce.o main.o parboil.o $(LINK_FLAG) -o $@

clean:
	rm -f *.o cp makelog *.s

cleanall: clean
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/