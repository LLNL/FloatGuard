# (c) 2007 The Board of Trustees of the University of Illinois.

# Rules common to all makefiles

# Commands to build objects from source file using C compiler
# with gcc

# gcc (default)
CC = hipcc
PLATFORM_CFLAGS = -x hip
  
CXX = hipcc
PLATFORM_CXXFLAGS = -x hip
  
LINKER = hipcc
PLATFORM_LDFLAGS = -lm -lpthread

