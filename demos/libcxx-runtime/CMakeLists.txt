cmake_minimum_required(VERSION 3.28)

project(libcxx_runtime LANGUAGES CXX)

add_executable(libcxx_runtime main.cpp)
target_compile_features(libcxx_runtime PRIVATE cxx_std_20)

if(NOT CMAKE_CROSSCOMPILING)
  if(NOT WIN32)
    target_compile_options(libcxx_runtime PRIVATE -fsanitize=address)
    target_link_options(libcxx_runtime PRIVATE -fsanitize=address)
  endif()
  add_custom_target(run_libcxx_runtime ALL
    DEPENDS libcxx_runtime COMMAND libcxx_runtime)
endif()
