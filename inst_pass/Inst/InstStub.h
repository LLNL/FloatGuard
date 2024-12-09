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

#ifndef EXP_FLAG_LOW 
#define EXP_FLAG_LOW (EXP_FLAG_TOTAL & 0x0000FFFF)
#endif

#ifndef EXP_FLAG_HIGH
#define EXP_FLAG_HIGH (EXP_FLAG_TOTAL & 0xFFFF0000)
#endif

#define ASM_SET_EXCEPTION_INTERNAL(LOW, HIGH) "s_setreg_imm32_b32 hwreg(HW_REG_MODE, 0, 16), " #LOW "\ns_setreg_imm32_b32 hwreg(HW_REG_MODE, 16, 16), " #HIGH " "
#define ASM_SET_EXCEPTION(_LOW, _HIGH) ASM_SET_EXCEPTION_INTERNAL(_LOW, _HIGH)

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
      asm volatile (
        ASM_SET_EXCEPTION(EXP_FLAG_LOW, EXP_FLAG_HIGH)
      );
  }

  __device__ void DISABLE_FP_EXCEPTION(RANDINT)
  {
      asm volatile (
        ASM_SET_EXCEPTION(0x02F0, 0x0000)
      );
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