#include <cstdio>

// Initialize stdout/stderr for ARM EABI bare metal systems
#if defined(__ARM_EABI__)
FILE* const stderr = nullptr;
FILE* const stdout = nullptr;
#endif
