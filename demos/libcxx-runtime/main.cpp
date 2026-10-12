// Checks that programs built with this toolchain run against a libc++ that
// matches its headers, including under AddressSanitizer.
//
// - Throwing std::bad_variant_access needs the vtable for
//   std::__bad_variant_access_with_msg, which LLVM 23's headers reference
//   but older system libc++ dylibs (e.g. macOS 26) don't export.
// - Locale use plus a static std::ofstream destroyed at exit aborts under
//   ASan if two libc++ copies are mixed in the process (bad-free in
//   std::locale::~locale). On macOS that happens when the executable exports
//   its weak libc++ symbols and dyld coalesces them with the system libc++
//   that the ASan runtime loads.
#include <fstream>
#include <iostream>
#include <locale>
#include <sstream>
#include <string>
#include <variant>

namespace {
std::ofstream report("libcxx-runtime-report.txt");
}  // namespace

int
main()
{
  std::variant<int, std::string> value = 1;
  try {
    (void)std::get<std::string>(value);
    std::cout << "expected std::bad_variant_access\n";
    return 1;
  } catch (std::bad_variant_access const& error) {
    report << "caught: " << error.what() << '\n';
  }

  std::ostringstream text;
  text.imbue(std::locale::classic());
  text << 3.25 << ' ' << 42;
  auto const& ctype = std::use_facet<std::ctype<char>>(std::locale());
  report << text.str() << ' ' << ctype.toupper('a') << '\n';

  std::cout << "libc++ runtime check passed" << std::endl;
  return 0;
}
