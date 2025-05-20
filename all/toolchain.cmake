# LLVM/Clang CMake toolchain file
# This file should be placed in the package and referenced in the conanfile.py

# Set system name for cross-compilation
# Valid options: Linux, Darwin (macOS), Windows, etc.
set(CMAKE_SYSTEM_NAME ${LLVM_CMAKE_SYSTEM_NAME})

# Set architecture name
set(CMAKE_SYSTEM_PROCESSOR ${LLVM_CMAKE_SYSTEM_PROCESSOR})

# LLVM installation path comes from the Conan package
set(LLVM_INSTALL_DIR $ENV{LLVM_INSTALL_DIR})

set(CMAKE_C_COMPILER_WORKS 1)
set(CMAKE_CXX_COMPILER_WORKS 1)

# Set compilers - Conan should have added bin to PATH already
set(CMAKE_C_COMPILER clang)
set(CMAKE_CXX_COMPILER clang++)
set(CMAKE_AR llvm-ar)
set(CMAKE_NM llvm-nm)
set(CMAKE_RANLIB llvm-ranlib)
set(CMAKE_OBJCOPY llvm-objcopy)
set(CMAKE_OBJDUMP llvm-objdump)
set(CMAKE_STRIP llvm-strip)

# Set target triple for cross-compilation
if(DEFINED LLVM_TARGET_TRIPLE)
  set(target_flags "-target ${LLVM_TARGET_TRIPLE}")
  set(CMAKE_C_FLAGS_INIT "${target_flags}")
  set(CMAKE_CXX_FLAGS_INIT "${target_flags}")
  set(CMAKE_EXE_LINKER_FLAGS_INIT "${target_flags}")
  set(CMAKE_SHARED_LINKER_FLAGS_INIT "${target_flags}")
  set(CMAKE_MODULE_LINKER_FLAGS_INIT "${target_flags}")
endif()

# Set sysroot if provided
if(DEFINED LLVM_SYSROOT)
  set(CMAKE_SYSROOT ${LLVM_SYSROOT})
  set(CMAKE_C_FLAGS_INIT "${CMAKE_C_FLAGS_INIT} --sysroot=${LLVM_SYSROOT}")
  set(CMAKE_CXX_FLAGS_INIT "${CMAKE_CXX_FLAGS_INIT} --sysroot=${LLVM_SYSROOT}")
  set(CMAKE_EXE_LINKER_FLAGS_INIT "${CMAKE_EXE_LINKER_FLAGS_INIT} --sysroot=${LLVM_SYSROOT}")
  set(CMAKE_SHARED_LINKER_FLAGS_INIT "${CMAKE_SHARED_LINKER_FLAGS_INIT} --sysroot=${LLVM_SYSROOT}")
  set(CMAKE_MODULE_LINKER_FLAGS_INIT "${CMAKE_MODULE_LINKER_FLAGS_INIT} --sysroot=${LLVM_SYSROOT}")
endif()

# Configuration for find_* commands
set(CMAKE_FIND_ROOT_PATH ${LLVM_INSTALL_DIR})
if(DEFINED LLVM_SYSROOT)
  list(APPEND CMAKE_FIND_ROOT_PATH ${LLVM_SYSROOT})
endif()

# Only search for libraries and includes in the target directories
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

# Set appropriate default compiler flags
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Add additional LLVM-specific flags if needed
if(DEFINED LLVM_EXTRA_FLAGS)
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${LLVM_EXTRA_FLAGS}")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${LLVM_EXTRA_FLAGS}")
endif()

# Ensure the RPATH is set correctly
if(APPLE)
  set(CMAKE_MACOSX_RPATH ON)
endif()
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH ON)
set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)
