SHELL=/bin/sh
BENCHMARK=sp
BENCHMARKU=SP

include ../config/make.def

OBJS =	sp.o \
	${COMMON}/c_print_results.o ${COMMON}/c_timers.o ${COMMON}/c_wtime.o

include ../sys/make.common

${PROGRAM}: config ${OBJS}
	${CLINK} ${CLINKFLAGS} -o ${PROGRAM} ${OBJS} ${C_LIB}

sp.o:		sp.cu npbparams.hpp
	${CCOMPILE} sp.cu

clean:
	- rm -f *.o *.s *.bc seq.txt *~ mputil*
	- rm -f npbparams.hpp core

cleanall: clean
	rm -f exp_flag.txt seq.txt inject_points.txt loc.txt