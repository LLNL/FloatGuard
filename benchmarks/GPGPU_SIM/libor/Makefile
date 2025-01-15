include ../shared.mk

libor: libor.cu
	$(NVCC) $^ $(NVCC_FLAGS) $(LINK_FLAG) -o $@

clean: $(SRC)
	rm -f libor makelog

