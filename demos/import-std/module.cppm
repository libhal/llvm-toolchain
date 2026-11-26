export module test_module;

import std;

namespace test {
export template<typename T>
T
sum(std::span<T const> values)
{
  return std::ranges::fold_left(values, T{}, std::plus{});
}
}
