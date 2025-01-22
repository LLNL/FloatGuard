/**
 * syrk.cu: This file is part of the PolyBench/GPU 1.0 test suite.
 *
 *
 * Contact: Scott Grauer-Gray <sgrauerg@gmail.com>
 * Will Killian <killian@udel.edu>
 * Louis-Noel Pouchet <pouchet@cse.ohio-state.edu>
 * Web address: http://www.cse.ohio-state.edu/~pouchet/software/polybench/GPU
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <assert.h>
#include <unistd.h>
#include <sys/time.h>
#include <hip/hip_runtime.h>

#define POLYBENCH_TIME 1

#include "syrk.cuh"
#include <polybench.h>
#include <polybenchUtilFuncts.h>

//define the error threshold for the results "not matching"
#define PERCENT_DIFF_ERROR_THRESHOLD 0.05

#define GPU_DEVICE 0

//#define RUN_ON_CPU


void init_arrays(int ni, int nj,
		DATA_TYPE *alpha,
		DATA_TYPE *beta,
		DATA_TYPE POLYBENCH_2D(C,NI,NI,ni,ni),
		DATA_TYPE POLYBENCH_2D(A,NI,NJ,ni,nj))
{
	int i, j;

	*alpha = 32412;
	*beta = 2123;
	for (i = 0; i < ni; i++)
	{
		for (j = 0; j < nj; j++)
		{
			A[i][j] = ((DATA_TYPE) i*j) / ni;
		}
	}

	for (i = 0; i < ni; i++)
	{
		for (j = 0; j < ni; j++)
		{
			C[i][j] = ((DATA_TYPE) i*j) / ni;
		}
	}
}


void syrk(int ni, int nj, DATA_TYPE alpha, DATA_TYPE beta, DATA_TYPE POLYBENCH_2D(A, NI, NJ, ni, nj), DATA_TYPE POLYBENCH_2D(C, NI, NI, ni, ni))
{
	int i, j, k;
	
	/*  C := alpha*A*A' + beta*C */
	for (i = 0; i < _PB_NI; i++)
	{
		for (j = 0; j < _PB_NI; j++)
		{
			C[i][j] *= beta;
		}
	}
	
	for (i = 0; i < _PB_NI; i++)
	{
		for (j = 0; j < _PB_NI; j++)
		{
			for (k = 0; k < _PB_NJ; k++)
			{
				C[i][j] += alpha * A[i][k] * A[j][k];
			}
		}
	}
}


void compareResults(int ni, DATA_TYPE POLYBENCH_2D(C, NI, NI, ni, ni), DATA_TYPE POLYBENCH_2D(C_outputFromGpu, NI, NI, ni, ni))
{
	int i,j,fail;
	fail = 0;

	// Compare C with D
	for (i=0; i<ni; i++)
	{
		for (j=0; j<ni; j++)
		{
			if (percentDiff(C[i][j], C_outputFromGpu[i][j]) > PERCENT_DIFF_ERROR_THRESHOLD)
			{
				fail++;
			}
		}
	}
	
	// print results
	printf("Non-Matching CPU-GPU Outputs Beyond Error Threshold of %4.2f Percent: %d\n", PERCENT_DIFF_ERROR_THRESHOLD, fail);
}


void GPU_argv_init()
{
	hipDeviceProp_t deviceProp;
	hipGetDeviceProperties(&deviceProp, GPU_DEVICE);
	printf("setting device %d with name %s\n",GPU_DEVICE,deviceProp.name);
	hipSetDevice( GPU_DEVICE );
	
	return;
}


__global__ void syrk_kernel(int ni, int nj, DATA_TYPE alpha, DATA_TYPE beta, DATA_TYPE *a, DATA_TYPE *c)
{
	/*  C := alpha*A*A' + beta*C */
	int j = blockIdx.x * blockDim.x + threadIdx.x;
	int i = blockIdx.y * blockDim.y + threadIdx.y;

	if ((i < _PB_NI) && (j < _PB_NI))
	{
		c[i * NI + j] *= beta;
		int k;		
		for(k=0; k < _PB_NJ; k++)
		{
			c[i * NI + j] += alpha * a[i * NJ + k] * a[j * NJ + k];
		}
	}
}


void syrkCuda(int ni, int nj, DATA_TYPE alpha, DATA_TYPE beta, DATA_TYPE POLYBENCH_2D(A, NI, NJ, ni, nj), DATA_TYPE POLYBENCH_2D(C, NI, NI, ni, ni), 
		DATA_TYPE POLYBENCH_2D(C_outputFromGpu, NI, NI, ni, ni))
{
	DATA_TYPE* A_gpu;
	DATA_TYPE* C_gpu;

	hipMalloc((void **)&A_gpu, sizeof(DATA_TYPE) * NI * NJ);
	hipMalloc((void **)&C_gpu, sizeof(DATA_TYPE) * NI * NI);
	hipMemcpy(A_gpu, A, sizeof(DATA_TYPE) * NI * NJ, hipMemcpyHostToDevice);
	hipMemcpy(C_gpu, C, sizeof(DATA_TYPE) * NI * NI, hipMemcpyHostToDevice);
	
	dim3 block(DIM_THREAD_BLOCK_X, DIM_THREAD_BLOCK_Y);
	dim3 grid((size_t)(ceil(((float)NI) / ((float)DIM_THREAD_BLOCK_X))), (size_t)ceil(((float)NI) / ((float)DIM_THREAD_BLOCK_Y)));

	/* Start timer. */
  	polybench_start_instruments;

	syrk_kernel<<<grid,block>>>(ni, nj, alpha, beta, A_gpu,C_gpu);
	hipDeviceSynchronize();

	/* Stop and print timer. */
	printf("GPU Time in seconds:\n");
  	polybench_stop_instruments;
 	polybench_print_instruments;

	hipMemcpy(C_outputFromGpu, C_gpu, sizeof(DATA_TYPE) * NI * NI, hipMemcpyDeviceToHost);

	hipFree(A_gpu);
	hipFree(C_gpu);
}


/* DCE code. Must scan the entire live-out data.
   Can be used also to check the correctness of the output. */
static
void print_array(int ni, DATA_TYPE POLYBENCH_2D(C,NI,NI,ni,ni))
{
  int i, j;

  for (i = 0; i < ni; i++)
    for (j = 0; j < ni; j++) {
	fprintf (stderr, DATA_PRINTF_MODIFIER, C[i][j]);
	if ((i * ni + j) % 20 == 0) fprintf (stderr, "\n");
    }
  fprintf (stderr, "\n");
}


int main(int argc, char *argv[])
{
	int ni, nj;
	if (argc == 2) 
	{
		switch (atoi(argv[1]))
		{
			case 0: ni = nj = 256; break;
			case 1: ni = nj = 512; break;
			case 2: ni = nj = 1024; break;
			case 3: ni = nj = 2048; break;
			case 4: ni = nj = 4096; break;
		}
	}
	else
	{
		ni = nj = 1024;
	}

	/* Variable declaration/allocation. */
	DATA_TYPE alpha;
	DATA_TYPE beta;

	POLYBENCH_2D_ARRAY_DECL(A,DATA_TYPE,NI,NJ,ni,nj);
  	POLYBENCH_2D_ARRAY_DECL(C,DATA_TYPE,NI,NI,ni,ni);
  	POLYBENCH_2D_ARRAY_DECL(C_outputFromGpu,DATA_TYPE,NI,NI,ni,ni);

	init_arrays(ni, nj, &alpha, &beta, POLYBENCH_ARRAY(C), POLYBENCH_ARRAY(A));
	
	GPU_argv_init();	
	syrkCuda(ni, nj, alpha, beta, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(C), POLYBENCH_ARRAY(C_outputFromGpu));

	#ifdef RUN_ON_CPU

		/* Start timer. */
	  	polybench_start_instruments;

		syrk(ni, nj, alpha, beta, POLYBENCH_ARRAY(A), POLYBENCH_ARRAY(C));

		/* Stop and print timer. */
		printf("CPU Time in seconds:\n");
  		polybench_stop_instruments;
 		polybench_print_instruments;

		compareResults(ni, POLYBENCH_ARRAY(C), POLYBENCH_ARRAY(C_outputFromGpu));

	#else //prevent dead code elimination

		polybench_prevent_dce(print_array(ni, POLYBENCH_ARRAY(C_outputFromGpu)));

	#endif //RUN_ON_CPU


	POLYBENCH_FREE_ARRAY(A);
  	POLYBENCH_FREE_ARRAY(C);
	POLYBENCH_FREE_ARRAY(C_outputFromGpu);

	return 0;
}

#include <polybench.c>