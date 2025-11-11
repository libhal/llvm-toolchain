# LLVM Toolchain Repo

A Conan tool package for the LLVM Toolchain (`clang`, `clang++`, `lld`). By adding
this tool package to your Conan build profile, your project will be cross-compiled
using the LLVM toolchain for embedded ARM Cortex-M targets.

## ✨ Key Features

- **Single cross-compiler**: LLVM can target multiple architectures with one toolchain
- **Modules support**: LLVM 20+ includes full C++20 modules support
- **Modern C++ standards**: Best-in-class support for C++20/23 features
- **Better diagnostics**: Clear, actionable error messages
- **Integrated tooling**: Includes clang-tidy, clang-format, and other development tools

## 📋 Supported Versions

- **LLVM 20.1.8** - Includes C++20 modules support (recommended)

## 🎯 Supported Architectures

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

All binaries are downloaded from the official
[LLVM GitHub Releases](https://github.com/llvm/llvm-project/releases).

## 🚀 Quick Start

To use the LLVM Toolchain for your application, install the pre-made compiler
profiles to your local `conan2` cache:

```bash
conan config install -sf conan/profiles/v1 -tf profiles https://github.com/libhal/llvm-toolchain.git
```

This provides profiles accessible via `-pr clang-20`. These profiles only include
compiler information. You'll need a "target" profile to actually build something.
The target profile must include `os=baremetal` and `arch` set to a valid architecture.

Add the following to a profile named `target_profile`:

```jinja2
[settings]
build_type=MinSizeRel
arch=cortex-m4f
os=baremetal
```

Now build your application using LLVM 20 for Cortex-M4F with MinSizeRel optimization:

```bash
conan build path/to/application -pr clang-20 -pr ./target_profile
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
llvm-toolchain/20.1.8
```

By adding `llvm-toolchain/20.1.8` to your profile, every dependency will use this
toolchain for compilation. The tool package should NOT be directly added to an
application's `conanfile.py`.

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

When you create the package, it downloads the compiler from the official LLVM releases
and stores it in your local Conan package cache:

```bash
conan create . --version 20.1.8
```

## 🎛️ Options

### `default_arch` (Default: `True`)

Automatically inject appropriate `-target`, `-mcpu`, and `-mfloat-abi` flags for
the `arch` defined in your build target profile.

For `cortex-m4`: `-target armv7em-none-eabi -mcpu=cortex-m4 -mfloat-abi=soft`
For `cortex-m4f`: `-target armv7em-none-eabihf -mcpu=cortex-m4 -mfloat-abi=hard -mfpu=fpv4-sp-d16`

### `lto` (Default: `True`)

Enable Link-Time Optimization with `-flto`.

### `fat_lto` (Default: `True`)

Enable `-ffat-lto-objects` for compatibility with linkers without LTO support.
Ignored if `lto` is `False`.

### `function_sections` (Default: `True`)

Enable `-ffunction-sections` to place each function in its own section for better
garbage collection at link time.

### `data_sections` (Default: `True`)

Enable `-fdata-sections` to place each data item in its own section for better
garbage collection at link time.

### `gc_sections` (Default: `True`)

Enable `--gc-sections` linker flag for garbage collection of unused sections.
