cmake_minimum_required(VERSION 3.12)
project(civ-pass)

execute_process(COMMAND which hipcc
                OUTPUT_VARIABLE HIPCC_PATH
                OUTPUT_STRIP_TRAILING_WHITESPACE)

file(REAL_PATH ${HIPCC_PATH} HIPCC_REAL_PATH)

# we need LLVM_HOME in order to automatically set LLVM_DIR
set(CMAKE_CXX_COMPILER hipcc)
set(LLVM_ROOT "/opt/rocm/llvm")
find_package(LLVM REQUIRED CONFIG)
string(REPLACE "/bin/hipcc" " " HIPCC_ROCM_PATH ${HIPCC_REAL_PATH})
message(STATUS "rocm path = ${HIPCC_ROCM_PATH}") 

set(LLVM_INCLUDE_DIRS "/opt/rocm/llvm/include")
set(LLVM_LIBRARY_DIRS "/opt/rocm/llvm/lib")

add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
link_directories(${LLVM_LIBRARY_DIRS})
if (${LLVM_VERSION_MAJOR} VERSION_GREATER_EQUAL 10)
    set(CMAKE_CXX_STANDARD 17)
endif ()

add_subdirectory(Inst)