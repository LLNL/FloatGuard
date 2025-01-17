include ../shared.mk

laplace3d: laplace3d.cu laplace3d_gold.cpp
	$(NVCC) $(NVCC_FLAGS) -c laplace3d_gold.cpp
	$(NVCC) $(NVCC_FLAGS) -c laplace3d.cu
	$(NVCC) laplace3d_gold.o laplace3d.o $(NVCC_FLAGS) $(LINK_FLAG) -o $@

clean: $(SRC)
	rm -f laplace3d makelog *.s

cleanall: clean
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/

