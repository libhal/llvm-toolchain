#include <cinttypes>
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

  return c;
}
