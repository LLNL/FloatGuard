SHELL=/bin/sh
BENCHMARK=bt
BENCHMARKU=BT

include ../config/make.def

OBJS =	bt.o \
	${COMMON}/c_print_results.o ${COMMON}/c_timers.o ${COMMON}/c_wtime.o

include ../sys/make.common

${PROGRAM}: config ${OBJS}
	${CLINK} ${CLINKFLAGS} -o ${PROGRAM} ${OBJS} ${C_LIB}

bt.o:             bt.cu npbparams.hpp
	${CCOMPILE} bt.cu

clean:
	- rm -f *.o *.s *.bc seq.txt *~ mputil*
	- rm -f  npbparams.hpp core

cleanall: clean
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/