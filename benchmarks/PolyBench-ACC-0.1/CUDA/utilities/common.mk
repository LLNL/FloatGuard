

ifndef $(INJECT_CODE_LLVM)
INJECT_CODE_LLVM = 0
endif

ifeq ($(INJECT_CODE_LLVM), 1)
INST_FLAGS = -g -fpass-plugin=${HOME}/FloatGuard/inst_pass/libInstPass.so \
			 -DEXP_FLAG_TOTAL=0x0005F2F0
else
INST_FLAGS = -g \
			 -DEXP_FLAG_TOTAL=0x0005F2F0
endif

FP_FLAGS = -DDATA_TYPE=double -DDATA_PRINTF_MODIFIER=\"%0.2lf\"

all:
	${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh  -O3 ${CUFILES} -I${PATH_TO_UTILS} -o ${EXECUTABLE} ${INST_FLAGS} ${FP_FLAGS} -DEXTRALARGE_DATASET
	
clean:
	rm -f *~ *.s *.exe* seq.txt 

cleanall: clean
	rm -r exp_flag.txt seq.txt inject_points.txt loc.txt asm_info/