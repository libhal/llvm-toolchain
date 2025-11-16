cmake_minimum_required(VERSION 3.40)

set(CMAKE_OSX_SYSROOT "")

project(demo LANGUAGES CXX)
add_executable(demo main.cpp)
target_compile_features(demo PRIVATE cxx_std_23)
