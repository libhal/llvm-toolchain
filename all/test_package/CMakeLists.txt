cmake_minimum_required(VERSION 3.15)

set(CMAKE_TOOLCHAIN_FILE ../toolchain.cmake)

# Add this to your test_package/CMakeLists.txt
message(STATUS "=== ENVIRONMENT VARIABLES ===")
execute_process(
    COMMAND ${CMAKE_COMMAND} -E environment
    OUTPUT_VARIABLE env_vars
)
message(STATUS "${env_vars}")

project(test_package LANGUAGES CXX)

add_executable(test_package main.cpp)
target_compile_options(test_package PRIVATE -stdlib=libc++)
