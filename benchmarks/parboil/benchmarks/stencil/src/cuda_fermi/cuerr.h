/***************************************************************************
 *cr
 *cr            (C) Copyright 2010 The Board of Trustees of the
 *cr                        University of Illinois
 *cr                         All Rights Reserved
 *cr
 ***************************************************************************/




#define CUERR { hipError_t err; \
  if ((err = hipGetLastError()) != hipSuccess) { \
  printf("CUDA error: %s, line %d\n", hipGetErrorString(err), __LINE__); \
  return -1; }}
