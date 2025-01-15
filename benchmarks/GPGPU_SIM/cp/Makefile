include ../shared.mk

cp: cuenergy_pre8_coalesce.cu main.cu parboil.c
	$(NVCC) $(NVCC_FLAGS) $^ $(LINK_FLAG) -o $@

clean:
	rm -f *.o cp makelog

