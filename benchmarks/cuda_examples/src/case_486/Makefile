#----------------------------------------
HIPCC    = ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh
HIPFLAGS = -g -O3 -DEXP_FLAG_TOTAL=0x0005F2F0
LINKFLAGS = -fgpu-rdc --hip-link 
#----------------------------------------

test: test.hip
	${HIPCC} ${HIPFLAGS} -c test.hip -o test.o
	${HIPCC} ${LINKFLAGS} -o test test.o 

run:
	./test `cat input.txt`

.PHONY: clean

clean:
	rm -f test *.o *.bc *.ll *.s

cleanall: clean
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/
