# CMake 4.5 builds the standard library's `std` module for any C++23 target
# it scans for modules, from the libc++.modules.json the toolchain points it
# at (CMAKE_CXX_STDLIB_MODULES_JSON for Cortex-M targets).
cmake_minimum_required(VERSION 4.5)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_SCAN_FOR_MODULES ON)
set(CMAKE_COLOR_DIAGNOSTICS ON)

project(demo LANGUAGES CXX)

add_executable(demo)

target_sources(demo PUBLIC
    FILE_SET CXX_MODULES
    TYPE CXX_MODULES

    FILES
    module.cppm

    PRIVATE
    main.cpp
)

if(NOT ${CMAKE_CROSSCOMPILING})
  add_custom_target(run_demo ALL DEPENDS demo COMMAND demo)
endif(NOT ${CMAKE_CROSSCOMPILING})

add_custom_target(copy_compile_commands ALL
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${CMAKE_BINARY_DIR}/compile_commands.json"
        "${CMAKE_SOURCE_DIR}/compile_commands.json"
        || ${CMAKE_COMMAND} -E true
    COMMENT "Copying compile_commands.json to source directory"
)
