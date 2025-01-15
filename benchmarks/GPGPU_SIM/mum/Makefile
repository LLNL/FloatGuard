include ../shared.mk

mum: mummergpu.o mummergpu_main.o mummergpu_gold.o suffix-tree.o PoolMalloc.o
	$(NVCC) $(NVCC_FLAGS) $^ $(LINK_FLAG) -o $@

mummergpu.o: mummergpu.cu
	$(NVCC) $(NVCC_FLAGS) -c $^

mummergpu_main.o: mummergpu_main.cpp
	$(CC) $(CC_FLAGS) -c $^

mummergpu_gold.o: mummergpu_gold.cpp
	$(CC) $(CC_FLAGS) -c $^

suffix-tree.o: suffix-tree.cpp
	$(CC) $(CC_FLAGS) -c $^

PoolMalloc.o: PoolMalloc.cpp
	$(CC) $(CC_FLAGS) -c $^
	
clean:
	rm -f *.o mummergpu
	rm -f mum makelog




