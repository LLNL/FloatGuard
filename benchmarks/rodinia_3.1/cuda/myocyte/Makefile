# Example
# target: dependencies
	# command 1
	# command 2
          # .
          # .
          # .
	# command n

# link objects(binaries) together
myocyte.out:		main.o
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh main.o ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o \
                                -o myocyte.out

# compile main function file into object (binary)
main.o:	define.c \
				main.cu \
				work.cu \
				solver.cu \
				embedded_fehlberg_7_8.cu \
				master.cu \
				kernel.cu \
				kernel_ecc.cu \
				kernel_cam.cu \
				kernel_fin.cu \
				work_2.cu \
				solver_2.cu \
				embedded_fehlberg_7_8_2.cu \
				kernel_2.cu \
				kernel_ecc_2.cu \
				kernel_cam_2.cu \
				kernel_fin_2.cu \
				file.c \
				timer.c
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh	$(INST_FLAGS) main.cu \
				-c -O3 -g

# delete all object files
clean_base:
	-rm *.o *.s *.out output.txt

clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/