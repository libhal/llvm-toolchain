# LLVM Toolchain Conan Package

A Conan tool package for the LLVM Toolchain (`clang`, `clang++`, `lld`). By
adding this tool package to your Conan build profile, your project can leverage
the LLVM toolchain for modern C++ development across multiple platforms and
architectures.

## ✨ Key Features

- **Single cross-compiler**: LLVM can target multiple architectures with one
  toolchain
- **Embedded ARM support**: Built-in support for ARM Cortex-M microcontrollers
  using the ARM LLVM Embedded Toolchain
- **Modules support**: LLVM 20+ includes full C++20 modules support
- **Modern C++ standards**: Best-in-class support for C++20/23 features
- **Better diagnostics**: Clear, actionable error messages
- **Integrated tooling**: Includes clang-tidy, clang-format, and other
  development tools

## 📋 Supported Versions & Host Platforms

All binaries are downloaded from official sources:

- Upstream LLVM from [LLVM GitHub Releases](https://github.com/llvm/llvm-project/releases)
- ARM Cortex-M targets from [ARM LLVM Embedded Toolchain](https://github.com/arm/arm-toolchain/releases)

### LLVM 20

| Platform | x86_64 | ARM64 |
| -------- | ------ | ----- |
| Linux    | ✅      | ✅     |
| macOS    | ❌      | ✅     |
| Windows  | ✅      | ✅     |

> [!IMPORTANT]
> This package uses version "20" to represent the most recent official releases
> from both upstream LLVM and the ARM LLVM Embedded Toolchain. However, the
> exact version numbers differ:
>
> - **Upstream LLVM**: Version 20.1.8 (for host platforms and non-Cortex-M targets)
> - **ARM Embedded Toolchain**: Version 20.1.0 (for ARM Cortex-M baremetal targets)
>
> Both versions are the latest official releases available at the time of
> packaging. The package automatically selects the appropriate variant based on
> your target architecture.

## 🚀 Quick Start

To use the LLVM Toolchain for your application, install the pre-made compiler
profiles to your local `conan2` cache:

```bash
conan config install -sf conan/profiles/v1 -tf profiles https://github.com/libhal/llvm-toolchain.git
```

This provides profiles accessible via `-pr llvm-20`. These profiles only
include compiler information. You'll need a "target" profile to actually build
something.

### Host Platform Profiles

For native development on your host platform:

```bash
# x86_64 Linux
conan build . -pr llvm-20 -pr linux_x86_64

# ARM64 Linux
conan build . -pr llvm-20 -pr linux_arm

# ARM64 macOS
conan build . -pr llvm-20 -pr mac_arm

# x86_64 Windows
conan build . -pr llvm-20 -pr windows_x86_64
```

### ARM Cortex-M Profiles

For embedded ARM Cortex-M development (cross-compilation):

```bash
# Cortex-M4 with hardware floating point
conan build . -pr llvm-20 -pr cortex-m4f

# Cortex-M7 with double-precision FPU
conan build . -pr llvm-20 -pr cortex-m7d

# Cortex-M33 with hardware floating point
conan build . -pr llvm-20 -pr cortex-m33f
```

## 🔗 Adding as a Dependency

For this tool package to work correctly, the toolchain **MUST** be added as a
dependency using `tool_requires` in at least one profile:

```jinja2
[settings]
compiler=clang
compiler.cppstd=23
compiler.libcxx=libc++
compiler.version=20

[tool_requires]
llvm-toolchain/20
```

By adding `llvm-toolchain/20` to your profile, every dependency will use
this toolchain for compilation. The tool package should NOT be directly added
to an application's `conanfile.py`.

Note that the profile above is missing the following settings:

- `os`
- `build_type`
- `arch`

### Host Platform Examples

For a Release build on an M1 (ARM CPU) Mac:

```plaintext
[settings]
arch=armv8
build_type=Release
os=Macos
```

For x86_64 Linux:

```plaintext
[settings]
arch=x86_64
build_type=Release
os=Linux
```

For x86_64 Windows:

```plaintext
[settings]
arch=x86_64
build_type=Release
os=Windows
```

### ARM Cortex-M Examples

For ARM Cortex-M4 with hardware floating point:

```plaintext
[settings]
arch=cortex-m4f
build_type=Release
os=baremetal
```

For ARM Cortex-M7 with double-precision FPU:

```plaintext
[settings]
arch=cortex-m7d
build_type=Release
os=baremetal
```

## 🧾 Using Pre-made Profiles

Install profiles into your local conan cache:

```bash
conan config install -sf conan/profiles/v1 -tf profiles https://github.com/libhal/llvm-toolchain.git
```

Or from a locally cloned repo:

```bash
conan config install -sf conan/profiles/v1 -tf profiles .
```

Profiles use `libc++` as the standard library (LLVM's C++ standard library implementation).

## 📦 Building & Installing the Tool Package

When you create the package, it downloads the appropriate compiler variant from
the official releases based on your build and target settings, then stores it
in your local Conan package cache:

```bash
# For host platform development
conan create . --version 20

# For ARM Cortex-M cross-compilation (downloads ARM Embedded variant)
conan create . -pr:b default -pr:h cortex-m4f -pr:h llvm-20 --version 20 --build-require
```

## 🎛️ Options

Example profile options:

```plaintext
[options]
llvm-toolchain/*:default_arch=True
llvm-toolchain/*:default_linker_script=True
llvm-toolchain/*:lto=True
llvm-toolchain/*:data_sections=True
llvm-toolchain/*:function_sections=True
llvm-toolchain/*:gc_sections=True
```

### `default_arch` (Default: `True`)

Automatically inject appropriate `-target`, `-mcpu`, and `-mfloat-abi` flags for
the `arch` defined in your build target profile.

Examples for ARM Cortex-M:

- For `cortex-m4`:
  - `-target armv7em-none-eabi`
  - `-mcpu=cortex-m4`
  - `-mfloat-abi=soft`
- For `cortex-m4f`:
  - `-target armv7em-none-eabihf`
  - `-mcpu=cortex-m4`
  - `-mfloat-abi=hard`
  - `-mfpu=fpv4-sp-d16`

### `default_linker_script` (Default: `True`)

Automatically specify the default linker script (`picolibcpp.ld`) to allow
projects without a linker script to link without error. If you specify your own
linker script(s) via the `-T` argument, the default linker script will be
ignored and your supplied linker script(s) will be used.

> [!NOTE]
> Disabling this flag is not necessary when building applications with custom
> linker scripts. Only use this if you have multiple custom linker scripts and
> want to override the default linker script supplied by this toolchain.

### `lto` (Default: `True`)

Enable Link-Time Optimization with `-flto`.

### `function_sections` (Default: `True`)

Enable `-ffunction-sections` to place each function in its own section for
better garbage collection at link time.

### `data_sections` (Default: `True`)

Enable `-fdata-sections` to place each data item in its own section for better
garbage collection at link time.

### `gc_sections` (Default: `True`)

Enable `--gc-sections` linker flag for garbage collection of unused sections.

## 🎯 Supported ARM Cortex-M Targets

The following embedded ARM Cortex-M architectures are fully supported:

- cortex-m0
- cortex-m0plus
- cortex-m1
- cortex-m3
- cortex-m4
- cortex-m4f
- cortex-m7
- cortex-m7f
- cortex-m7d
- cortex-m23
- cortex-m33
- cortex-m33f
- cortex-m35p
- cortex-m35pf
- cortex-m55
- cortex-m85

> [!NOTE]
> The architecture names may have trailing characters indicating floating point support:
>
> - `f` indicates single precision (32-bit) hard float
> - `d` indicates double precision (64-bit) hard float

These targets use the [ARM LLVM Embedded Toolchain](https://github.com/arm/arm-toolchain),
which is specifically optimized for bare-metal ARM Cortex-M development and
includes optimized C/C++ libraries for embedded systems.

## 🔮 Future Target Support

### Other Architectures

Support for additional architectures (RISC-V, AVR, etc.) is planned. These will
use the upstream LLVM toolchain. Contributions are welcome!

## 🔖 Interpreting Versions

The "Release" version represents the version of the `conanfile.py` and its
`conandata.yml`. Versions follow [SEMVER 2](https://semver.org/).

1. Patch version increments if:
   1. A non-feature change or fix has been applied to the conan recipe
2. Minor version increments if:
   1. A new option is made available via the recipe
   2. New versions of LLVM made available within `conandata.yml`
3. Major number increments if:
   1. An option is removed
   2. Command line arguments change in such a way as to not be a bug fix but to
      seriously change the semantics of a program
   3. A toolchain file is:
      1. Removed
      2. Added and enforced for all downstream users that meaningfully changes
         the semantics or compilation of a program

### Version Transparency

The package version (e.g., "20") represents a collection of related LLVM
toolchain releases:

- **Upstream LLVM**: Used for host platforms (Linux, macOS, Windows) and
  non-Cortex-M cross-compilation targets. Currently version 20.1.8.
- **ARM Embedded Toolchain**: Used for ARM Cortex-M baremetal targets.
  Currently version 20.1.0.

While these version numbers don't match exactly, both represent the latest
official releases from their respective sources. The package automatically
selects the appropriate variant based on your target architecture, ensuring you
always get the correct toolchain for your build.

## 🤝 Contributing

### Adding a New LLVM Version

To add support for a new LLVM version to this package, follow these steps:

#### 1. Download Official Binaries

Download the official LLVM prebuilt binaries from the [LLVM GitHub Releases](https://github.com/llvm/llvm-project/releases) page. Look for the release tagged as `llvmorg-X.X.X` and download the appropriate archives for each supported platform:

- **Linux x86_64**: `LLVM-X.X.X-Linux-X64.tar.xz`
- **Linux ARM64**: `LLVM-X.X.X-Linux-ARM64.tar.xz`
- **macOS ARM64**: `LLVM-X.X.X-macOS-ARM64.tar.xz`
- **Windows x86_64**: `clang+llvm-X.X.X-x86_64-pc-windows-msvc.tar.xz`
- **Windows ARM64**: `clang+llvm-X.X.X-aarch64-pc-windows-msvc.tar.xz` (if available)

For ARM Cortex-M support, download from the [ARM Toolchain Releases](https://github.com/arm/arm-toolchain/releases):

- **Linux x86_64**: `ATfE-X.X.X-Linux-x86_64.tar.xz`
- **Linux ARM64**: `ATfE-X.X.X-Linux-AArch64.tar.xz`
- **macOS Universal**: `ATfE-X.X.X-Darwin-universal.dmg`
- **Windows x86_64**: `ATfE-X.X.X-Windows-x86_64.zip`

> [!NOTE]
> Not all platforms may be available for every LLVM version. Only download what's officially provided.

#### 2. Calculate SHA256 Checksums

Calculate the SHA256 checksums for all downloaded archives:

```bash
cd /path/to/downloaded/archives
shasum -a 256 *.tar.xz *.dmg *.zip
```

Save these checksums - you'll need them for the next step.

#### 3. Update `conandata.yml`

Add a new version entry to [`all/conandata.yml`](all/conandata.yml) with the URLs and SHA256 checksums:

```yaml
sources:
  "X":
    "upstream":
      "Linux":
        "x86_64":
          url: "https://github.com/llvm/llvm-project/releases/download/llvmorg-X.X.X/LLVM-X.X.X-Linux-X64.tar.xz"
          sha256: "<checksum>"
        "armv8":
          url: "https://github.com/llvm/llvm-project/releases/download/llvmorg-X.X.X/LLVM-X.X.X-Linux-ARM64.tar.xz"
          sha256: "<checksum>"
      "Macos":
        "armv8":
          url: "https://github.com/llvm/llvm-project/releases/download/llvmorg-X.X.X/LLVM-X.X.X-macOS-ARM64.tar.xz"
          sha256: "<checksum>"
      "Windows":
        "x86_64":
          url: "https://github.com/llvm/llvm-project/releases/download/llvmorg-X.X.X/clang+llvm-X.X.X-x86_64-pc-windows-msvc.tar.xz"
          sha256: "<checksum>"
    "arm-embedded":
      "Linux":
        "x86_64":
          url: "https://github.com/arm/arm-toolchain/releases/download/release-X.X.X-ATfE/ATfE-X.X.X-Linux-x86_64.tar.xz"
          sha256: "<checksum>"
        "armv8":
          url: "https://github.com/arm/arm-toolchain/releases/download/release-X.X.X-ATfE/ATfE-X.X.X-Linux-AArch64.tar.xz"
          sha256: "<checksum>"
      "Macos":
        "armv8":
          url: "https://github.com/arm/arm-toolchain/releases/download/release-X.X.X-ATfE/ATfE-X.X.X-Darwin-universal.dmg"
          sha256: "<checksum>"
        "x86_64":
          url: "https://github.com/arm/arm-toolchain/releases/download/release-X.X.X-ATfE/ATfE-X.X.X-Darwin-universal.dmg"
          sha256: "<checksum>"
      "Windows":
        "x86_64":
          url: "https://github.com/arm/arm-toolchain/releases/download/release-X.X.X-ATfE/ATfE-X.X.X-Windows-x86_64.zip"
          sha256: "<checksum>"
```

Only include platforms that have official prebuilt binaries available.

#### 4. Update README.md

Add the new version to the [Supported Versions & Host Platforms](#-supported-versions--host-platforms) section in this README. Be transparent about any version differences between upstream LLVM and the ARM Embedded Toolchain.

#### 5. Test the Package

Build and test the package locally for both host and ARM Cortex-M targets:

```bash
# Test host platform build
conan create all --version X

# Test ARM Cortex-M cross-compilation
conan create all -pr:b default -pr:h cortex-m4f -pr:h llvm-X --version X --build-require
```

This downloads the binaries, verifies checksums, and creates the package.

#### 6. Build and Run the Demo

Install the toolchain profiles and build the demo application:

```bash
# Install toolchain profiles
conan config install -tf profiles/ -sf conan/profiles/v1/ .

# Build the demo for host platform
conan build demo -pr llvm-X -pr linux_x86_64 --build=missing

# Build the demo for ARM Cortex-M (cross-compilation)
conan build demo -pr llvm-X -pr cortex-m4f --build=missing
```

> [!NOTE]
> Replace `linux_x86_64` and `cortex-m4f` with your platform's profile.
> Available profiles are in the `conan/profiles/v1/` directory.

#### 7. Submit a Pull Request

Once you've verified everything works:

1. Commit your changes to `all/conandata.yml` and `README.md`
2. Submit a pull request with a clear description of the version being added
3. Include any platform-specific notes or limitations
4. Note any version mismatches between upstream LLVM and ARM Embedded Toolchain
