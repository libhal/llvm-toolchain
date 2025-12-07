#include <cstdio>

// Initialize stdout/stderr for ARM EABI bare metal systems
// These are needed for <print> and std::println
#if defined(__ARM_EABI__)
FILE* const stderr = nullptr;
FILE* const stdout = nullptr;
extern "C"
{
  void _exit(int)
  {
    while (true) {
      continue;
    }
  }
  int isatty(int)
  {
    return 1;
  }
}
#endif