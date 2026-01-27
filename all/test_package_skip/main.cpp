#include <cstdio>

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

// Test Native testing
//
//    VERBOSE=1 conan test all/test_package llvm-toolchain/20
//
// Use arm embedded to build stm32f103c8
//
//    VERBOSE=1 conan test -pr stm32f103c8 -pr hal/tc/llvm-20 all/
//    test_package llvm-toolchain/20
//
