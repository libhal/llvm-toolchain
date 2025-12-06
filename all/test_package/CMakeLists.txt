cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

add_executable(test_package main.cpp)
target_compile_options(test_package PRIVATE -stdlib=libc++)
# target_link_options(test_package PRIVATE -Tpicolibcpp.ld)
