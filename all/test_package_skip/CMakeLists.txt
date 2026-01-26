cmake_minimum_required(VERSION 3.15)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(test_package LANGUAGES CXX)

add_executable(test_package main.cpp)
target_compile_options(test_package PRIVATE -stdlib=libc++)
