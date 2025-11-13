# LLVM Toolchain Conan Packagegit

A Conan tool package for the LLVM Toolchain (`clang`, `clang++`, `lld`). By
adding this tool package to your Conan build profile, your project can leverage
the LLVM toolchain for modern C++ development.

## ✨ Key Features

- **Single cross-compiler**: LLVM can target multiple architectures with one
  toolchain
- **Modules support**: LLVM 20+ includes full C++20 modules support
- **Modern C++ standards**: Best-in-class support for C++20/23 features
- **Better diagnostics**: Clear, actionable error messages
- **Integrated tooling**: Includes clang-tidy, clang-format, and other
  development tools

## 📋 Supported Versions

- **LLVM 20.1.8** - Includes C++20 modules support (recommended)

## 💻 Supported Host Platforms

Currently, this toolchain package is only supported on:

- **macOS 14** (Apple Silicon / ARM64)
- **macOS 15** (Apple Silicon / ARM64)

> [!NOTE]
> Support for Linux (x86_64, ARM64) and macOS Intel is planned for future
> releases.

All binaries are downloaded from the official
[LLVM GitHub Releases](https://github.com/llvm/llvm-project/releases).

## 🚀 Quick Start

To use the LLVM Toolchain for your application, install the pre-made compiler
profiles to your local `conan2` cache:

```bash
conan config install -sf conan/profiles/v1 -tf profiles https://github.com/libhal/llvm-toolchain.git
```

This provides profiles accessible via `-pr clang-20`. These profiles only
include compiler information. You'll need a "target" profile to actually build
something.

> [!NOTE]
> Cross-compilation target support (such as ARM Cortex-M) is currently in
> development. See the [Future Target Support](#-future-target-support) section
> for planned architectures.

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
llvm-toolchain/20.1.8
```

By adding `llvm-toolchain/20.1.8` to your profile, every dependency will use
this toolchain for compilation. The tool package should NOT be directly added
to an application's `conanfile.py`.

Note that the profile above is missing the following settings:

- `os`
- `build_type`
- `arch`

For example, for an Release build on an M1 (ARM CPU) Mac, you'd use the
following profile:

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

When you create the package, it downloads the compiler from the official LLVM
releases and stores it in your local Conan package cache:

```bash
conan create . --version 20.1.8
```

## 🎛️ Options

Example profile options:

```plaintext
[options]
llvm-toolchain/*:default_arch=False
llvm-toolchain/*:lto=True
llvm-toolchain/*:data_sections=True
llvm-toolchain/*:function_sections=True
llvm-toolchain/*:gc_sections=True
```

### `default_arch` (Default: `True`)

Automatically inject appropriate `-target`, `-mcpu`, and `-mfloat-abi` flags for
the `arch` defined in your build target profile.

Example (for future ARM Cortex-M support):

- For `cortex-m4`:
  - `-target armv7em-none-eabi`
  - `-mcpu=cortex-m4`
  - `-mfloat-abi=soft`
- For `cortex-m4f`:
  - `-target armv7em-none-eabihf`
  - `-mcpu=cortex-m4`
  - `-mfloat-abi=hard`
  - `-mfpu=fpv4-sp-d16`

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

## 🔮 Future Target Support

### Windows

We plan to add support for windows binaries when we get a chance.

### ARM Cortex-M

The following embedded ARM Cortex-M architectures are planned for future
support:

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
- cortex-m35pf
- cortex-m55
- cortex-m85

> [!NOTE]
> The architecture names may have trailing characters indicating floating point support:
>
> - `f` indicates single precision (32-bit) hard float
> - `d` indicates double precision (64-bit) hard float
