#----------------------------------------
HIPCC    = ${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh
HIPFLAGS = -g -O3
LINKFLAGS = -fgpu-rdc --hip-link 
#----------------------------------------

div0: div0.cpp
	${HIPCC} ${HIPFLAGS} -c div0.cpp -o div0.o
	${HIPCC} ${LINKFLAGS} div0.o  -o div0

.PHONY: clean

clean_base:
	rm -f div0 *.o *.bc *.ll *.s 

clean: clean_base
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/