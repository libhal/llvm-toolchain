cmake_minimum_required(VERSION 3.40)

set(CMAKE_CXX_COMPILER_WORKS TRUE)
set(CMAKE_C_COMPILER_WORKS TRUE)

project(demo LANGUAGES CXX)
add_executable(demo main.cpp)
# target_compile_features(demo PRIVATE cxx_std_23)

if(NOT ${CMAKE_CROSSCOMPILING})
  add_custom_target(run_demo ALL DEPENDS demo COMMAND demo)
endif(NOT ${CMAKE_CROSSCOMPILING})
