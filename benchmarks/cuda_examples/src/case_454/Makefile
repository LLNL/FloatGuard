#----------------------------------------
HIPCC    = hipcc #${HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh
HIPFLAGS = -g -O3
LINKFLAGS = -fgpu-rdc --hip-link 
#----------------------------------------

ifeq ($(INJECT_CODE_LLVM), 1)
HIPFLAGS += -fpass-plugin=${HOME}/FloatGuard/inst_pass/libInstPass.so
endif

ifeq ($(INJECT_CODE_CLANG), 1)
HIPFLAGS += -c -emit-llvm -Xclang -load -Xclang ${HOME}/FloatGuard/clang-examples/FloatGuard-plugin/FloatGuard-plugin.so -Xclang -plugin -Xclang inject-fp-exception 
endif

test: test.hip
	${HIPCC} ${HIPFLAGS} -c test.hip -o test.o
	${HIPCC} ${LINKFLAGS} -o test test.o ${HOME}/FloatGuard/inst_pass/Inst/InstStub.o

run:
	./test `cat input.txt`

.PHONY: clean

clean:
	rm -f test *.o *.bc *.ll *.s