#include "hip/hip_runtime.h"
#include "cudacommon.h"
#define _USE_MATH_DEFINES
#include <math.h>
#include <float.h>
#include <hip/hip_runtime.h>
#include <hipfft/hipfft.h>
#include "OptionParser.h"
#include "fftlib.h"

int fftDevice = -1;

bool do_dp;

//#define USE_CUFFT

#ifdef USE_CUFFT
hipfftHandle plan;
// Arrange blocks into 2D grid that fits into the GPU (for powers of two only)
inline dim3 grid2D(const int nblocks)
{
    int slices = 1;
    while (nblocks/slices > 65535)
    {
        slices *= 2;
    }
    return dim3(nblocks/slices, slices);
}

void printCUFFTError(const hipfftResult res)
{
    if (res != HIPFFT_SUCCESS)
    {
        cout << "CUFFT Error: ";
        if (res == HIPFFT_INVALID_PLAN)
        {
            cout << "Invalid Plan.\n";
        }
        else if (res == HIPFFT_INVALID_VALUE)
        {
            cout << "Invalid Value.\n";
        }
        else if (res == HIPFFT_INTERNAL_ERROR)
        {
            cout << "Internal Error .\n";
        }
        else if (res == HIPFFT_EXEC_FAILED)
        {
            cout << "FFT Exec failed.\n";
        }
        else if (res == HIPFFT_SETUP_FAILED)
        {
            cout << "Setup failed.\n";
        }
        else if (res == HIPFFT_UNALIGNED_DATA)
        {
            cout << "Unaligned data (unused).\n";
        }
    }
}

#else
#include "codelets.h"
#endif

template <class T2> __global__ void
chk512_device(const T2* __restrict__ work, const int half_n_cmplx,
    char* __restrict__ fail)
{
    int i, tid = threadIdx.x;
    T2 a[8], b[8];

    work += (blockIdx.y * gridDim.x + blockIdx.x) * 512 + tid;

    for (i = 0; i < 8; i++)
    {
        a[i] = work[i*64];
    }

    for (i = 0; i < 8; i++)
    {
        b[i] = work[half_n_cmplx+i*64];
    }

    for (i = 0; i < 8; i++)
    {
        if (a[i].x != b[i].x || a[i].y != b[i].y)
        {
            *fail = 1;
        }
    }
}


template <class T2> __global__ void
norm512_device(T2* __restrict__ work)
{
    int i, tid = threadIdx.x;

    work += (blockIdx.y * gridDim.x + blockIdx.x) * 512 + tid;

    for (i = 0; i < 8; i++)
    {
        work[i*64].x /= 512;
        work[i*64].y /= 512;
    }
}


void
init(OptionParser& op, const bool _do_dp, const int n_ffts)
{
    do_dp = _do_dp;
    if (fftDevice == -1)
    {
        if (op.getOptionVecInt("device").size() > 0)
        {
            fftDevice = op.getOptionVecInt("device")[0];
        }
        else
        {
            fftDevice = 0;
        }
        hipSetDevice(fftDevice);
        hipGetDevice(&fftDevice);
    }
#ifdef USE_CUFFT
    hipfftResult res;
    cerr << "init: initing plan, n_ffts=" << n_ffts << endl;
    if (do_dp)
    {
        res = hipfftPlan1d(&plan, 512, HIPFFT_Z2Z, n_ffts);
    }
    else
    {
        res = hipfftPlan1d(&plan, 512, HIPFFT_C2C, n_ffts);
    }
    if (res != HIPFFT_SUCCESS)
    {
        cout << "CUFFT Error in plan.\n";
    }
    else
    {
        cerr <<  "success...\n";
    }
#endif

}


void
forward(void* work, const int n_ffts)
{
#ifdef USE_CUFFT
    hipfftResult res;
    if (do_dp)
    {
        res = hipfftExecZ2Z(plan, (hipfftDoubleComplex*)work,
            (hipfftDoubleComplex*)work, HIPFFT_FORWARD);
    }
    else
    {
        res = hipfftExecC2C(plan, (hipfftComplex*)work,
            (hipfftComplex*)work, HIPFFT_FORWARD);
    }
    printCUFFTError(res);
    hipDeviceSynchronize();
    CHECK_CUDA_ERROR();
#else
    if (do_dp)
    {
        FFT512_device<double2, double><<<grid2D(n_ffts), 64>>>((double2*)work);
    }
    else
    {
        FFT512_device<float2, float><<<grid2D(n_ffts), 64>>>((float2*)work);
    }
    hipDeviceSynchronize();
    CHECK_CUDA_ERROR();
#endif
}


void
inverse(void* work, const int n_ffts)
{
#ifdef USE_CUFFT
    hipfftResult res;
    if (do_dp)
    {
        res = hipfftExecZ2Z(plan, (hipfftDoubleComplex*)work,
            (hipfftDoubleComplex*)work, HIPFFT_BACKWARD);
    }
    else
    {
        res = hipfftExecC2C(plan, (hipfftComplex*)work,
            (hipfftComplex*)work, HIPFFT_BACKWARD);
    }
    printCUFFTError(res);

    // normalize data...
    if (do_dp)
    {
        norm512_device<double2><<<grid2D(n_ffts), 64>>>((double2*)work);
    }
    else
    {
        norm512_device<float2><<<grid2D(n_ffts), 64>>>((float2*)work);
    }
    hipDeviceSynchronize();
    CHECK_CUDA_ERROR();
#else
    if (do_dp)
    {
        IFFT512_device<double2, double><<<grid2D(n_ffts), 64>>>((double2*)work);
    }
    else
    {
        IFFT512_device<float2, float><<<grid2D(n_ffts), 64>>>((float2*)work);
    }
    hipDeviceSynchronize();
    CHECK_CUDA_ERROR();
    // normalization built in to inverse...
#endif
}


int
check(void* work, void* check, const int half_n_ffts, const int half_n_cmplx)
{
    char result;

    if (do_dp)
    {
        chk512_device<double2><<<grid2D(half_n_ffts), 64>>>(
            (double2*)work, half_n_cmplx, (char*)check);
    }
    else
    {
        chk512_device<float2><<<grid2D(half_n_ffts), 64>>>(
            (float2*)work, half_n_cmplx, (char*)check);
    }
    hipMemcpy(&result, check, 1, hipMemcpyDeviceToHost);
    CHECK_CUDA_ERROR();

    return result;
}


void
allocHostBuffer(void** bufferp, unsigned long bytes)
{
    hipHostMalloc(bufferp, bytes);
    CHECK_CUDA_ERROR();
}

void
allocDeviceBuffer(void** bufferp, unsigned long bytes)
{
    hipMalloc(bufferp, bytes);
    CHECK_CUDA_ERROR();
}

void
freeHostBuffer(void* buffer)
{
    hipHostFree(buffer);
    CHECK_CUDA_ERROR();
}


void
freeDeviceBuffer(void* buffer)
{
    hipFree(buffer);
}

void
copyToDevice(void* to_device, const void* from_host,
    const unsigned long bytes)
{
    hipMemcpy(to_device, from_host, bytes, hipMemcpyHostToDevice);
    CHECK_CUDA_ERROR();
}

void
copyFromDevice(void* to_host, const void* from_device,
    const unsigned long bytes)
{
    hipMemcpy(to_host, from_device, bytes, hipMemcpyDeviceToHost);
    CHECK_CUDA_ERROR();
}

