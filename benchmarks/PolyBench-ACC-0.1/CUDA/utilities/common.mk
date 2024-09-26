RANDINT = $(shell python3 -c 'from random import randint; print(randint(1000000000, 9999999999));')

ifndef $(INJECT_CODE_LLVM)
INJECT_CODE_LLVM = 0
endif

ifeq ($(INJECT_CODE_LLVM), 1)
INST_FLAGS = -g -include ${HOME}/hipec/inst_pass/Inst/InstStub.h -fpass-plugin=${HOME}/hipec/inst_pass/libInstPass.so -DRANDINT=${RANDINT} \
			 -DEXP_FLAG_TOTAL=0x0005F2F0
else
INST_FLAGS = -g -include ${HOME}/hipec/inst_pass/Inst/InstStub.h -DRANDINT=${RANDINT} \
			 -DEXP_FLAG_TOTAL=0x0005F2F0
endif

FP_FLAGS = -DDATA_TYPE=double -DDATA_PRINTF_MODIFIER=\"%0.2lf\"

all:
	hipcc ${HOME}/hipec/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_mini ${INST_FLAGS} ${FP_FLAGS} -DMINI_DATASET
	hipcc ${HOME}/hipec/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_small ${INST_FLAGS} ${FP_FLAGS} -DSMALL_DATASET
	hipcc ${HOME}/hipec/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_standard ${INST_FLAGS} ${FP_FLAGS} -DSTANDARD_DATASET
	hipcc ${HOME}/hipec/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_large ${INST_FLAGS} ${FP_FLAGS} -DLARGE_DATASET
	hipcc ${HOME}/hipec/inst_pass/Inst/InstStub.o -O3 -ffast-math ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE}_extralarge ${INST_FLAGS} ${FP_FLAGS} -DEXTRALARGE_DATASET
	
clean:
	rm -f *~ *.exe* seq.txt