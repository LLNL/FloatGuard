ifndef $(DEBUG)
DEBUG = 0
endif

# LLVM path: in the docker environment it is empty (root)
# export LLVM_PATH=/collab/usr/global/tools/fpchecker/llvm-12.0.0-install

# C++ compiler
CXX		= hipcc

# llvm-config location
APPLE_LDFLAGS = #-Wl,-flat_namespace -Wl,-undefined -Wl,suppress

# Passed to compiler
SRC_DIR		?= $(PWD)
ifeq ($(DEBUG), 1)
COMMON_FLAGS	= -Wall -O0 -g
else
COMMON_FLAGS	= -Wall -O3 -g
endif

HIPCC_PATH = $(realpath $(shell which hipcc))
HIPCC_ROCM_PATH = $(HIPCC_PATH:/bin/hipcc=)

LLVM_CXXFLAGS = -I$(HIPCC_ROCM_PATH)/llvm/include -std=c++17 -fno-exceptions -fno-rtti -DBUILD_EXAMPLES -D_GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_LIMIT_MACROS
LLVM_CPPFLAGS = -DBUILD_EXAMPLES -D_GNU_SOURCE -D__STDC_CONSTANT_MACROS -D__STDC_FORMAT_MACROS -D__STDC_LIMIT_MACROS
LLVM_LDFLAGS = 


LDFLAGS		+= $(LLVM_LDFLAGS) $(APPLE_LDFLAGS)
CXXFLAGS	+= $(COMMON_FLAGS) -fPIC -DFPC_DEBUG $(LLVM_CXXFLAGS) 
CPPFLAGS	+= $(LLVM_CPPFLAGS) -I$(SRC_DIR)

SHARED_LIB_OPT  = -shared

# Installation path
prefix		= /lib/

PROG		= FloatGuard-plugin.so

all: $(PROG)

source:
	$(CXX) $(CXXFLAGS) -o FloatGuard-plugin.o -c FloatGuard-plugin.cpp
	$(CXX) $(CXXFLAGS) -o TransformMutations.o -c TransformMutations.cpp
	$(CXX) $(CXXFLAGS) -o utils.o -c utils.cpp
	
	
$(PROG): source
	$(CXX) $(CXXFLAGS) $(LDFLAGS) $(SHARED_LIB_OPT) -o $(PROG) FloatGuard-plugin.o TransformMutations.o utils.o

	@echo "Clang plugin build success."

install:
	cp $(PROG) $(prefix)
	@echo "Clang plugin installation success."

clean:
	$(RM) *.o

cleanall:
	$(RM) *.o $(PROG)
