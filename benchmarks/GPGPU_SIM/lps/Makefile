include ../shared.mk

laplace3d: laplace3d.cu laplace3d_gold.cpp
	$(NVCC) $^ $(NVCC_FLAGS) $(LINK_FLAG) -o $@

clean: $(SRC)
	rm -f laplace3d makelog

