#include <cstdio>

// Initialize stdout/stderr for ARM EABI bare metal systems
#if defined(__ARM_EABI__)
FILE* const stderr = nullptr;
FILE* const stdout = nullptr;
#endif

int
main()
{
  std::puts("\n========== RUNNING DEMO ==========");
  std::puts("LLVM Toolchain Demo!");
  std::puts("👋 Hello, 🌐 World");
  std::puts("========== DEMO FINISHED ==========\n");
  return 0;
}