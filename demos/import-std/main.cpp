import std;
import test_module;

int
main()
{
  std::array const integers{ 5, 6 };
  std::array const decimals{ 7.2, 2.5 };

  std::println("\n========== RUNNING IMPORT STD DEMO ==========");
  std::println("LLVM Toolchain Demo!");
  std::println("👋 Hello, 🌐 World");
  std::println("sum({}) = {}", integers, test::sum<int>(integers));
  std::println("sum({}) = {}", decimals, test::sum<double>(decimals));
  std::println("========== DEMO FINISHED ==========\n");
  return 0;
}
