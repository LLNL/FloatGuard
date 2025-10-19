cmake_minimum_required(VERSION 3.10)
project(div0 LANGUAGES CXX)

# Set HIP compiler
set(CMAKE_CXX_COMPILER $ENV{HOME}/FloatGuard/gdb_script/hipcc_wrapper.sh)

# Linker flags
set(LINKFLAGS -fgpu-rdc --hip-link)

# Add the executable
add_executable(div0 div0.cpp)

# Compile and link using HIPCC
set(CMAKE_CXX_FLAGS "-g -O3")

# Clean target
set_directory_properties( PROPERTIES
    ADDITIONAL_MAKE_CLEAN_FILES "*.bc *.ll"
)