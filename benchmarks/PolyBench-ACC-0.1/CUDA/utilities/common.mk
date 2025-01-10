

ifndef $(INJECT_CODE_LLVM)
INJECT_CODE_LLVM = 0
endif

ifeq ($(INJECT_CODE_LLVM), 1)
INST_FLAGS = -g -include ${HOME}/FloatGuard/inst_pass/Inst/InstStub.h -fpass-plugin=${HOME}/FloatGuard/inst_pass/libInstPass.so \
			 -DEXP_FLAG_TOTAL=0x0005F2F0
else
INST_FLAGS = -g -include ${HOME}/FloatGuard/inst_pass/Inst/InstStub.h \
			 -DEXP_FLAG_TOTAL=0x0005F2F0
endif

FP_FLAGS = -DDATA_TYPE=double -DDATA_PRINTF_MODIFIER=\"%0.2lf\"

all:
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_mini ${INST_FLAGS} ${FP_FLAGS} -DMINI_DATASET
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_small ${INST_FLAGS} ${FP_FLAGS} -DSMALL_DATASET
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_standard ${INST_FLAGS} ${FP_FLAGS} -DSTANDARD_DATASET
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_large ${INST_FLAGS} ${FP_FLAGS} -DLARGE_DATASET
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_extralarge ${INST_FLAGS} ${FP_FLAGS} -DEXTRALARGE_DATASET
	
clean:
	rm -f *~ *.s *.exe* seq.txt 

cleanall: clean
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/