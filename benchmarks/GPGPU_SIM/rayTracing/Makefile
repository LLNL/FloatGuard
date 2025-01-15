include ../shared.mk

rayTracing: rayTracing.o EasyBMP.o makebmp.o
	$(NVCC) $(NVCC_FLAGS) $^ $(LINK_FLAG) -o $@
	
rayTracing.o: rayTracing.cu
	$(NVCC) $(NVCC_FLAGS) $(LINK_FLAG) -c $^

EasyBMP.o: EasyBMP.cpp
	$(CC) $(CC_FLAGS) -c $^ $(NVCC_INCLUDE)

makebmp.o: makebmp.cpp
	$(CC) $(CC_FLAGS) -c $^ $(NVCC_INCLUDE)
	
clean:
	rm -f *.o reduction
	rm -f rayTracing makelog
