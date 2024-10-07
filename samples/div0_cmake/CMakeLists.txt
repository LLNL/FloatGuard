cmake_minimum_required(VERSION 3.10)
project(div0 LANGUAGES CXX)

# Set HIP compiler
set(HIPCC hipcc)

# Generate a random number using Python
execute_process(COMMAND python3 -c "from random import randint; print(randint(1000000000, 9999999999));"
                OUTPUT_VARIABLE RANDINT
                OUTPUT_STRIP_TRAILING_WHITESPACE)

# Common HIP flags
set(HIPFLAGS -g -O3 -include ${HOME}/hipec/inst_pass/Inst/InstStub.h)

# Linker flags
set(LINKFLAGS -fgpu-rdc --hip-link)

# Condition for LLVM-based injection
if(INJECT_CODE_LLVM)
    list(APPEND HIPFLAGS -fpass-plugin=${HOME}/hipec/inst_pass/libInstPass.so)
endif()

# Condition for Clang-based injection
if(INJECT_CODE_CLANG)
    list(APPEND HIPFLAGS -c -emit-llvm -Xclang -load -Xclang ${HOME}/hipec/clang-examples/hipec-plugin/hipec-plugin.so -Xclang -plugin -Xclang inject-fp-exception)
endif()

# Add the executable
add_executable(div0 div0.cpp)

# Compile and link using HIPCC
target_compile_options(div0 PRIVATE ${HIPFLAGS} -DRANDINT=${RANDINT})
target_link_libraries(div0 PRIVATE ${LINKFLAGS} ${HOME}/hipec/inst_pass/Inst/InstStub.o)

# Clean target
set_directory_properties( PROPERTIES
    ADDITIONAL_MAKE_CLEAN_FILES "*.bc *.ll"
)