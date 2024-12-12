#include "hip/hip_runtime.h"

__global__ void
kernel_int (int *global_memory, int a, int b)
{
  *global_memory = a / b;
}

__global__ void
kernel_fp (int *global_memory, float a, float b)
{
  int fret = (float)a / (float)b;
  *global_memory = fret;
}

__global__ void
kernel_mixed (int *global_memory, int a, int b)
{
  int fret = a / b;
  fret = fret + (float)a / (float)b;
  *global_memory = fret;
}

int
main (int argc, char* argv[])
{
int *global_memory;
  hipMalloc (&global_memory, 4);
kernel_int<<<1, 1>>> (global_memory, 1, 0);
  hipDeviceSynchronize();
kernel_fp<<<1, 1>>> (global_memory, 1, 0);
  hipDeviceSynchronize();
kernel_mixed<<<1, 1>>> (global_memory, 1, 0);
  hipDeviceSynchronize ();
  return 0;
}