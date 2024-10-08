cmake_minimum_required(VERSION 3.12)
project(civ-pass)

execute_process(COMMAND which hipcc
                OUTPUT_VARIABLE HIPCC_PATH
                OUTPUT_STRIP_TRAILING_WHITESPACE)
file(REAL_PATH ${HIPCC_PATH} HIPCC_REAL_PATH)
string(REPLACE "/bin/hipcc" "" HIPCC_ROCM_PATH ${HIPCC_REAL_PATH})
message(STATUS "rocm path = ${HIPCC_ROCM_PATH}") 

# we need LLVM_HOME in order to automatically set LLVM_DIR
set(CMAKE_CXX_COMPILER hipcc)
set(LLVM_ROOT "${HIPCC_ROCM_PATH}/llvm")
find_package(LLVM REQUIRED CONFIG)

message(STATUS "llvm root = ${LLVM_ROOT}") 

set(LLVM_INCLUDE_DIRS "${HIPCC_ROCM_PATH}/llvm/include")
set(LLVM_LIBRARY_DIRS "${HIPCC_ROCM_PATH}/llvm/lib")

add_definitions(${LLVM_DEFINITIONS})
include_directories(${LLVM_INCLUDE_DIRS})
link_directories(${LLVM_LIBRARY_DIRS})
if (${LLVM_VERSION_MAJOR} VERSION_GREATER_EQUAL 10)
    set(CMAKE_CXX_STANDARD 17)
endif ()

add_subdirectory(Inst)