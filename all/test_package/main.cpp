#include <cstdio>

// Initialize stdout/stderr for ARM EABI bare metal systems
#if defined(__ARM_EABI__)
FILE* const stderr = nullptr;
FILE* const stdout = nullptr;
#endif

int
main()
{
  int a = 5;
  int b = 12;
  int c = a + b;

  std::puts("Hello, world!");
  std::printf("a = %d, b = %d\n", a, b);
  std::printf("a + b = c = %d\n", c);

  return 0;
}

// Use arm embedded to build stm32f103c8
//
//    VERBOSE=1 conan test -pr stm32f103c8 -pr hal/tc/llvm-19.1.5 all/
//    test_package llvm-toolchain/19.1.5
//
// Test Native building using x64 binary to cross build to armv8
//
//    VERBOSE=1 conan test all/test_package llvm-toolchain/19.1.5