#----------------------------------------
HIPCC    = hipcc
RANDINT = $(shell python3 -c 'from random import randint; print(randint(1000000000, 9999999999));')
HIPFLAGS = -g -O3 -include ${HOME}/FloatGuard/inst_pass/Inst/InstStub.h 
LINKFLAGS = -fgpu-rdc --hip-link 
#----------------------------------------

ifeq ($(INJECT_CODE_LLVM), 1)
HIPFLAGS += -fpass-plugin=${HOME}/FloatGuard/inst_pass/libInstPass.so
endif

ifeq ($(INJECT_CODE_CLANG), 1)
HIPFLAGS += -c -emit-llvm -Xclang -load -Xclang ${HOME}/FloatGuard/clang-examples/FloatGuard-plugin/FloatGuard-plugin.so -Xclang -plugin -Xclang inject-fp-exception 
endif

div0: div0.cpp
	${HIPCC} ${HIPFLAGS} -DRANDINT=${RANDINT} -c div0.cpp -o div0.o
	${HIPCC} ${LINKFLAGS} div0.o ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o -o div0

.PHONY: clean

clean:
	rm -f div0 *.o *.bc *.ll
