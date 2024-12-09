#include "hip/hip_runtime.h"

#ifndef _INST_STUB_H_
#define _INST_STUB_H_

#define SET_FP_EXCEPTION_INTERNAL(_x) setfpexception_##_x()
#define SET_FP_EXCEPTION(_x) SET_FP_EXCEPTION_INTERNAL(_x)

#define ENABLE_FP_EXCEPTION_INTERNAL(_x) enablefpexception_##_x()
#define ENABLE_FP_EXCEPTION(_x) ENABLE_FP_EXCEPTION_INTERNAL(_x)

#define DISABLE_FP_EXCEPTION_INTERNAL(_x) disablefpexception_##_x()
#define DISABLE_FP_EXCEPTION(_x) DISABLE_FP_EXCEPTION_INTERNAL(_x)

#define FP_EXCEPTION_ENABLED_CONSTANT_INTERNAL(_x) fp_exception_enabled_##_x
#define FP_EXCEPTION_ENABLED_CONSTANT(_x) FP_EXCEPTION_ENABLED_CONSTANT_INTERNAL(_x)

__device__ int FP_EXCEPTION_ENABLED_CONSTANT(RANDINT)[1];

//#define XSTR(x) STR(x)
//#define STR(x) #x
//#pragma message "The value of RANDINT: " XSTR(RANDINT)

#ifndef EXP_FLAG_TOTAL
#define EXP_FLAG_TOTAL 0x0004D2F0
#endif

extern "C"
{
  __device__ void SET_FP_EXCEPTION(RANDINT)
  {
    uint32_t total = (1 - FP_EXCEPTION_ENABLED_CONSTANT(RANDINT) [0]) * 0x02F0 + FP_EXCEPTION_ENABLED_CONSTANT(RANDINT) [0] * EXP_FLAG_TOTAL;
    #ifndef NO_BRANCH
    if (total != 0x02F0) {
    #endif
      asm volatile ("s_setreg_b32 hwreg(HW_REG_MODE, 0, 32), %0" : "=s"(total));
    #ifndef NO_BRANCH
    }
    #endif
  }

  __device__ void ENABLE_FP_EXCEPTION(RANDINT)
  {
    uint32_t total = EXP_FLAG_TOTAL;
    asm volatile ("s_setreg_b32 hwreg(HW_REG_MODE, 0, 32), %0" : "=s"(total));
  }

  __device__ void DISABLE_FP_EXCEPTION(RANDINT)
  {
    uint32_t total = 0x02F0;
    asm volatile ("s_setreg_b32 hwreg(HW_REG_MODE, 0, 32), %0" : "=s"(total));
  }

  extern int get_fp_exception_enabled(char* func, void* rip);
  extern void init_fp_exception_sequence();
}

[[gnu::used, gnu::noinline, clang::optnone]]
static void set_fp_exception_enabled(char* func)
{
    //static int param = 0;
    int param = get_fp_exception_enabled(func, __builtin_return_address(0));
    init_fp_exception_sequence();
    //printf("set fp exception enabled: %d %x\n", (bool)param, __builtin_return_address(0));
    hipMemcpyToSymbol(HIP_SYMBOL(FP_EXCEPTION_ENABLED_CONSTANT(RANDINT)), &param, sizeof(param));    
}

#endif //_INST_STUB_H_