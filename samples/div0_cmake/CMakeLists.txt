cmake_minimum_required(VERSION 3.10)
project(div0 LANGUAGES CXX)

# Set HIP compiler
set(CMAKE_CXX_COMPILER hipcc)

# Generate a random number using Python
execute_process(COMMAND python3 -c "from random import randint; print(randint(1000000000, 9999999999));"
                OUTPUT_VARIABLE RANDINT
                OUTPUT_STRIP_TRAILING_WHITESPACE)

# Linker flags
set(LINKFLAGS -fgpu-rdc --hip-link)

# Add the executable
add_executable(div0 div0.cpp)

# Compile and link using HIPCC
set(CMAKE_CXX_FLAGS "-g -O3 -include $ENV{HOME}/FloatGuard/inst_pass/Inst/InstStub.h -DRANDINT=${RANDINT}")

# Condition for LLVM-based injection
if(INJECT_CODE_LLVM)
    string(APPEND CMAKE_CXX_FLAGS " -fpass-plugin=$ENV{HOME}/FloatGuard/inst_pass/libInstPass.so")
endif()

# Condition for Clang-based injection
if(INJECT_CODE_CLANG)
    string(APPEND CMAKE_CXX_FLAGS " -c -emit-llvm -Xclang -load -Xclang $ENV{HOME}/FloatGuard/clang-examples/FloatGuard-plugin/FloatGuard-plugin.so -Xclang -plugin -Xclang inject-fp-exception")
endif()

target_link_libraries(div0 PRIVATE ${LINKFLAGS} $ENV{HOME}/FloatGuard/inst_pass/Inst/InstStub.o)

# Clean target
set_directory_properties( PROPERTIES
    ADDITIONAL_MAKE_CLEAN_FILES "*.bc *.ll"
)