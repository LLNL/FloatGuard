include ../shared.mk

libor: libor.cu
	$(NVCC) $^ $(NVCC_FLAGS) $(LINK_FLAG) -o $@

clean: $(SRC)
	rm -f libor makelog *.s

cleanall: clean
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/

