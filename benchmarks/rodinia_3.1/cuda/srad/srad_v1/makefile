include ../../../common/make.config

CC := ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh

# Example
# target: dependencies
	# command 1
	# command 2
          # .
          # .
          # .
	# command n

# link objects(binaries) together
a.out:		main.o
	$(CC)	main.o \
				-o srad

# compile main function file into object (binary)
main.o: 	main.cu \
				define.c \
				graphics.c \
				extract_kernel.cu \
				prepare_kernel.cu \
				reduce_kernel.cu \
				srad_kernel.cu \
				srad2_kernel.cu \
				compress_kernel.cu
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh	$(INST_FLAGS) main.cu \
				-c -O3

# delete all object files
clean:
	rm *.o srad
