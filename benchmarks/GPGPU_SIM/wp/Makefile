include ../shared.mk


XXX = 8
YYY = 8
##################### gcc/gfortran ###############
CC      = gcc
FC      = gfortran
FCFLAGS = -fconvert=big-endian -frecord-marker=4 -ffree-form
OPT     =  -O3
#NVCC    = $(CUDA_DIR)/bin/nvcc -DCUDA
#LD      = $(FC)
LD      = $(NVCC)
LDOPT   = 
##################################################
# do not change this definition, change the one further down
FLOAT   = float
RWORDSIZE = 4
##################### cuda location ##############
# eces-shell
#CUDALIBPATH =  ~/emu/cuda/lib
# ncsa
#CUDALIBPATH =  /usr/local/cuda/lib
#LIBCUBLAS = $(CUDALIBPATH)/libcublas.so
#LIBCUBLASEMU = $(CUDALIBPATH)/libcublasemu.so


########################  THIS SECTION YOU CAN CHANGE ##################
#
# Hard coded number of levels  (35 for conus, 28 for jan00)
MKX = 28

# uncomment this to use FLOAT4 data type (optimization)
#FLOAT4 = -DFLOAT_4=4 

# this must always be defined but they do not do anything unless
# other settings are set

#PHASE   = -cuda --compiler-options -fno-strict-aliasing  
PHASE   =
NVOPT   = -DXXX=$(XXX) -DYYY=$(YYY) -DMKX=$(MKX) $(NVCC_FLAGS)


ROOTBINDIR ?= bin
BINDIR     ?= $(ROOTBINDIR)
BINSUBDIR  := release
TARGETDIR  := $(BINDIR)/$(BINSUBDIR)
ROOTOBJDIR ?= obj
LIBDIR     := $(NVIDIA_COMPUTE_SDK_LOCATION)/lib
COMMONDIR  := $(NVIDIA_COMPUTE_SDK_LOCATION)/common
INTERMED_FILES := *.cpp*.i *.cpp*.ii *.cu.c *.cudafe*.* *.fatbin.c *.cubin *.hash
CUDAHOME=$(CUDA_DIR)

GPGPULINK = $(LINK_FLAG)  -L/usr/lib/gcc/x86_64-linux-gnu/11 -lgfortran -lm -lz -ldl -lstdc++ $(NEWLIBDIR) $(LIB) # /usr/lib64/libstdc++.so.6 
.SUFFIXES :

#all : vanilla wp compare_snaps
all : wp 

wp : module_mp_wsm5.o  wsm5_gpu_f.o wsm5_f.o libmassv.o microclock.o
	$(NVCC) -o wp $(LDOPT) $^ $(LIBCUBLAS) $(GPGPULINK)

wsm5_f.o : wsm5.cu
	m4 wsm5.cu | sed "s/float/$(FLOAT)/g" > wsm5_f.cu
	$(NVCC)  $(NVOPT)  -c wsm5_f.cu

wsm5_gpu_f.o: wsm5_gpu.cu spt.h
	m4 wsm5_gpu.cu | ./spt.pl | sed "s/float/$(FLOAT)/g" > wsm5_gpu_f.cu
	$(NVCC)  $(NVOPT)  -c wsm5_gpu_f.cu

libmassv.o : libmassv.F
	$(FC) -E -C -P libmassv.F > libmassv.f90
	$(FC) -c $(OPT) $(FCFLAGS) libmassv.f90

microclock.o : microclock.c
	$(CC) -c $(CFLAGS) -DMKX=$(MKX) microclock.c

vanilla : module_mp_wsm5.F libmassv.o microclock.o
	$(FC) -E -C -P $(DEBUGDEBUG) -DRWORDSIZE=$(RWORDSIZE) module_mp_wsm5.F > module_mp_wsm5.f90
	$(FC) -c $(OPT) $(FCFLAGS) module_mp_wsm5.f90
	$(LD) -o wsm5_driver_vanilla $(LDOPT) module_mp_wsm5.o libmassv.o microclock.o $(LIBCUBLASEMU) $(GPGPULINK)

module_mp_wsm5.o: module_mp_wsm5.F
	$(FC) -E -C -P $(DEBUGDEBUG) -DRUN_ON_GPU -DRWORDSIZE=$(RWORDSIZE) module_mp_wsm5.F > module_mp_wsm5.f90
	$(FC) -c $(OPT) $(FCFLAGS) module_mp_wsm5.f90

compare_snaps : compare_snaps.F
	cp compare_snaps.F compare_snaps.f90
	$(FC) -o compare_snaps $(FCFLAGS) compare_snaps.f90
	rm -f compare_snaps.f90

clean :
	rm -f *.o *.cu.cpp *.f.cu wsm5_driver_* *.mod *.f90 compare_snaps gpgpu_inst_stats.txt snap_gpu_010 gpgpu_inst_stats.txt *.log *.ptx
	rm -f $(TARGETDIR)/WP
	rm -rf wp
	rm -rf makelog
	make clean_imm
clean_imm :
	rm -f $(INTERMED_FILES)

tar: 
	tar cvf wsm5gpu_`date +"%Y%m%d"`.tar *.cu *.F *.h *.m4 *.pl makefile
