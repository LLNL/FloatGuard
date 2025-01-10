SHELL=/bin/sh
BENCHMARK=mg
BENCHMARKU=MG

include ../config/make.def

OBJS = mg.o ${COMMON}/c_print_results.o  \
       ${COMMON}/c_${RAND}.o ${COMMON}/c_timers.o ${COMMON}/c_wtime.o

include ../sys/make.common

${PROGRAM}: config ${OBJS}
	${CLINK} ${CLINKFLAGS} -o ${PROGRAM} ${OBJS} ${C_LIB}

mg.o:		mg.cu npbparams.hpp 
	${CCOMPILE} mg.cu

clean:
	- rm -f *.o *.s *.bc seq.txt *~ 
	- rm -f npbparams.hpp core

cleanall: clean
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/