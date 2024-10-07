#----------------------------------------

HIPCC    = hipcc
HIPFLAGS = -g -O3 -fpass-plugin=../inst_pass/build/Inst/libInstPass.so
LINKFLAGS = 
#----------------------------------------

vector_addition:
	${HIPCC} ${HIPFLAGS} -c vector_addition.cpp -o vector_addition.o
	${HIPCC} ${LINKFLAGS} -fgpu-rdc --hip-link vector_addition.o -o vector_addition

.PHONY: clean

clean:
	rm -f vector_addition *.o *.bc *.ll
