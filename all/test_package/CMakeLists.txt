cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

project(test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Set RPATH settings
set(CMAKE_SKIP_BUILD_RPATH FALSE)           # Use RPATH in the build tree
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)    # Use INSTALL_RPATH instead of BUILD_RPATH
set(CMAKE_INSTALL_RPATH "/Users/kammce/.conan2/p/b/llvm-c4ae407487c8c/p/lib")  # Set the RPATH
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE) # Add paths of linked libraries to RPATH

# For macOS specifically
if(APPLE)
  set(CMAKE_MACOSX_RPATH TRUE)
endif()

# Get the macOS SDK path
execute_process(
  COMMAND xcrun --show-sdk-path
  OUTPUT_VARIABLE MACOS_SDK_PATH
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

add_executable(test_package main.cpp)

# Add both the LLVM lib directory and the system lib directory
target_link_directories(test_package PRIVATE
  /Users/kammce/.conan2/p/b/llvm-c4ae407487c8c/p/lib
  ${MACOS_SDK_PATH}/usr/lib
)

# Add sysroot flags to explicitly use the SDK
target_compile_options(test_package PRIVATE
  --sysroot=${MACOS_SDK_PATH}
)

target_link_options(test_package PRIVATE
  --sysroot=${MACOS_SDK_PATH}
)

# Set RPATH-related properties
set_target_properties(test_package PROPERTIES
  SKIP_BUILD_RPATH FALSE
  BUILD_WITH_INSTALL_RPATH TRUE
  INSTALL_RPATH "/Users/kammce/.conan2/p/b/llvm-c4ae407487c8c/p/lib"
  INSTALL_RPATH_USE_LINK_PATH TRUE
  MACOSX_RPATH TRUE
)