PROG        = libInstPass.so
MF_PATH=$(realpath $(dir $(lastword $(MAKEFILE_LIST))))

default: main

mk_workspace:
	mkdir -p $(MF_PATH)/build

main: mk_workspace
	cd $(MF_PATH)/build && cmake $(MF_PATH) && make
	cp $(MF_PATH)/build/Inst/$(PROG) $(MF_PATH)
	cd $(MF_PATH)/Inst && make -f Makefile.stub clean && make -f Makefile.stub

clean: mk_workspace
	rm -r $(MF_PATH)/build

cleanall: mk_workspace
	cd $(MF_PATH)/Inst && make -f Makefile.stub clean
	rm -r $(MF_PATH)/build
	rm -r $(MF_PATH)/$(PROG)