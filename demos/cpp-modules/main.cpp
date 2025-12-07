#include <print>

import test_module;

int
main()
{
  std::println("\n========== RUNNING MODULES DEMO ==========");
  std::println("LLVM Toolchain Demo!");
  std::println("👋 Hello, 🌐 World");
  std::println("sum(5, 6) = {}", test::sum(5, 6));
  std::println("sum(7.2, 2.5) = {}", test::sum(7.2, 2.5));
  std::println("========== DEMO FINISHED ==========\n");
  return 0;
}
