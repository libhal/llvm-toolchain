# LLVM/Clang CMake toolchain file for embedded ARM targets
# This toolchain file is configured by Conan to work with baremetal targets

# Append current directory to CMAKE_MODULE_PATH for device-specific cmake modules
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR})

# Skip compiler test which tends to fail for cross-compilation
set(CMAKE_CXX_COMPILER_WORKS TRUE)
set(CMAKE_C_COMPILER_WORKS TRUE)

# Force system to Generic & ARM for embedded targets
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

# Target definition
set(TOOLCHAIN clang)

# Perform compiler test with static library
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

# Set toolchain compilers - Conan adds LLVM bin to PATH
set(CMAKE_C_COMPILER clang${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_CXX_COMPILER clang++${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_ASM_COMPILER clang${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_AR llvm-ar${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_SIZE_UTIL llvm-size${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_OBJDUMP llvm-objdump${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_OBJCOPY llvm-objcopy${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_RANLIB llvm-ranlib${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_NM llvm-nm${CMAKE_EXECUTABLE_SUFFIX})
set(CMAKE_STRIP llvm-strip${CMAKE_EXECUTABLE_SUFFIX})

# Configure find_* commands for cross-compilation
set(CMAKE_FIND_ROOT_PATH ${CMAKE_PREFIX_PATH} ${CMAKE_BINARY_DIR})
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
