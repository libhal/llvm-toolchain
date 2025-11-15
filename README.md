# LLVM Toolchain Conan Package

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

## 📋 Supported Versions & Host Platforms

All binaries are downloaded from the official
[LLVM GitHub Releases](https://github.com/llvm/llvm-project/releases).

### LLVM 20.1.8

| Platform | x86_64 | ARM64 |
| -------- | ------ | ----- |
| Linux    | ✅      | ✅     |
| macOS    | ❌      | ✅     |
| Windows  | ✅      | ✅     |

### LLVM 19.1.7

| Platform | x86_64 | ARM64 |
| -------- | ------ | ----- |
| Linux    | ✅      | ✅     |
| macOS    | ⚠️¹     | ⚠️¹    |
| Windows  | ✅      | ❌     |

¹ *Binaries available but cause segmentation faults when running demos*

## 🚀 Quick Start

To use the LLVM Toolchain for your application, install the pre-made compiler
profiles to your local `conan2` cache:

```bash
conan config install -sf conan/profiles/v1 -tf profiles https://github.com/libhal/llvm-toolchain.git
```

This provides profiles accessible via `-pr llvm-20.1.8`. These profiles only
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

For x86_64 Windows:

```plaintext
[settings]
arch=x86_64
build_type=Release
os=Windows
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
      seriously change the semantics of a program. An example would be to force
   3. A toolchain file is
      1. Removed
      2. Added and enforced for all downstream users that meaningfully changes
         the semantics or compilation of a program.

## 🤝 Contributing

### Adding a New LLVM Version

To add support for a new LLVM version to this package, follow these steps:

#### 1. Download Official Binaries

Download the official LLVM prebuilt binaries from the [LLVM GitHub Releases](https://github.com/llvm/llvm-project/releases) page. Look for the release tagged as `llvmorg-X.X.X` and download the appropriate archives for each supported platform:

- **Linux x86_64**: `LLVM-X.X.X-Linux-X64.tar.xz` or `clang+llvm-X.X.X-x86_64-linux-gnu-*.tar.xz`
- **Linux ARM64**: `LLVM-X.X.X-Linux-ARM64.tar.xz` or `clang+llvm-X.X.X-aarch64-linux-gnu.tar.xz`
- **macOS x86_64**: `LLVM-X.X.X-macOS-X64.tar.xz` (if available)
- **macOS ARM64**: `LLVM-X.X.X-macOS-ARM64.tar.xz`
- **Windows x86_64**: `clang+llvm-X.X.X-x86_64-pc-windows-msvc.tar.xz`
- **Windows ARM64**: `clang+llvm-X.X.X-aarch64-pc-windows-msvc.tar.xz` (if available)

> [!NOTE]
> Not all platforms may be available for every LLVM version. Only download what's officially provided.

#### 2. Calculate SHA256 Checksums

Calculate the SHA256 checksums for all downloaded archives:

```bash
cd /path/to/downloaded/archives
shasum -a 256 *.tar.xz
```

Save these checksums - you'll need them for the next step.

#### 3. Update `conandata.yml`

Add a new version entry to [`all/conandata.yml`](all/conandata.yml) with the URLs and SHA256 checksums:

```yaml
sources:
  "X.X.X":
    "Linux":
      "x86_64":
        url: "https://github.com/llvm/llvm-project/releases/download/llvmorg-X.X.X/LLVM-X.X.X-Linux-X64.tar.xz"
        sha256: "<checksum>"
      "armv8":
        url: "https://github.com/llvm/llvm-project/releases/download/llvmorg-X.X.X/clang+llvm-X.X.X-aarch64-linux-gnu.tar.xz"
        sha256: "<checksum>"
    "Macos":
      "armv8":
        url: "https://github.com/llvm/llvm-project/releases/download/llvmorg-X.X.X/LLVM-X.X.X-macOS-ARM64.tar.xz"
        sha256: "<checksum>"
    "Windows":
      "x86_64":
        url: "https://github.com/llvm/llvm-project/releases/download/llvmorg-X.X.X/clang+llvm-X.X.X-x86_64-pc-windows-msvc.tar.xz"
        sha256: "<checksum>"
```

Only include platforms that have official prebuilt binaries available.

#### 4. Update README.md

Add the new version to the [Supported Versions & Host Platforms](#-supported-versions--host-platforms) section in this README:

```markdown
### LLVM X.X.X

| Platform | x86_64 | ARM64 |
| -------- | ------ | ----- |
| Linux    | ✅      | ✅     |
| macOS    | ❌      | ✅     |
| Windows  | ✅      | ✅     |
```

Use ✅ for supported platforms and ❌ for unsupported ones.

#### 5. Test the Package

Build and test the package locally:

```bash
conan create all --version X.X.X
```

This downloads the binaries, verifies checksums, and creates the package.

#### 6. Build and Run the Demo

Install the toolchain profiles and build the demo application:

```bash
# Install toolchain profiles
conan config install -tf profiles/ -sf conan/profiles/v1/ .

# Build the demo (use the version you're adding)
conan build demo -pr llvm-X.X.X -pr linux-x86_64 \
  --build=missing -c tools.build:skip_test=True

# Run the demo to verify it works
./demo/build/Release/demo
```

> [!NOTE]
> Replace `linux-x86_64` with your platform's profile. Available
> profiles are in the `conan/profiles/v1/` directory.

#### 7. Submit a Pull Request

Once you've verified everything works:

1. Commit your changes to `all/conandata.yml` and `README.md`
2. Submit a pull request with a clear description of the version being added
3. Include any platform-specific notes or limitations
