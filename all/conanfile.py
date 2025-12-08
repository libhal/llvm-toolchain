#!/usr/bin/python
#
# Copyright 2024 - 2025 Khalil Estell and the libhal contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
from pathlib import Path
from conan import ConanFile
from conan.tools.files import get, download, copy, chmod
from conan.errors import ConanInvalidConfiguration


class LLVMToolchainPackage(ConanFile):
    name = "llvm-toolchain"
    license = "Apache-2.0 WITH LLVM-exception"
    homepage = "https://releases.llvm.org/"
    description = "LLVM Toolchain for cross-compilation targeting various architectures"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "application"
    build_policy = "missing"
    short_paths = True

    options = {
        "default_arch": [True, False],
        "default_linker_script": [True, False],
        "lto": [True, False],
        "function_sections": [True, False],
        "data_sections": [True, False],
        "gc_sections": [True, False],
        "require_cmake": [True, False],
        "require_ninja": [True, False],
        "use_semihosting": [True, False],
    }

    default_options = {
        "default_arch": True,
        "default_linker_script": True,
        "lto": True,
        "function_sections": True,
        "data_sections": True,
        "gc_sections": True,
        "require_cmake": True,
        "require_ninja": True,
        "use_semihosting": True
    }

    options_description = {
        "default_arch": "Automatically inject architecture-appropriate -target and -mcpu arguments into compilation flags.",
        "lto": "Enable LTO support in binaries and intermediate files (.o and .a files)",
        "default_linker_script": "Automatically specify what the default linker script in order to allow projects without a linker script to link without error. If the user specifies their own linker script(s) via the -T argument, that default linker script will be ignored and the supplied linker script(s) will be used. Disabling this flag is not necessary when building applications with custom linker scripts. Only use this if you have multiple custom linker scripts and a default linker script you'd like to override against the supplied one from this toolchain library.",
        "lto": "Enable LTO support in binaries and intermediate files (.o and .a files)",
        "function_sections": "Enable -ffunction-sections which splits each function into their own subsection allowing link time garbage collection.",
        "data_sections": "Enable -fdata-sections which splits each statically defined block memory into their own subsection allowing link time garbage collection.",
        "gc_sections": "Enable garbage collection at link stage. Only useful if at least function_sections and data_sections is enabled.",
        "require_cmake": "Automatically add cmake/[^4.1.2] as a transitive build requirement.",
        "require_ninja": "Automatically add ninja/[^1.13.1] as a transitive build requirement and configure CMake to use Ninja as the generator.",
        "use_semihosting": "Inject command line flags to enable semihosting for your architecture. This is only used when the os=baremetal.",
    }

    def validate(self):
        supported_build_operating_systems = ["Linux", "Macos", "Windows"]
        if not self.settings_build.os in supported_build_operating_systems:
            raise ConanInvalidConfiguration(
                f"The build os '{self.settings_build.os}' is not supported. "
                "Pre-compiled binaries are only available for "
                f"{supported_build_operating_systems}."
            )

        supported_build_architectures = {
            "Linux": ["armv8", "x86_64"],
            "Macos": ["armv8", "x86_64"],
            "Windows": ["armv8", "x86_64"],
        }

        if (
            not self.settings_build.arch
            in supported_build_architectures[str(self.settings_build.os)]
        ):
            build_os = str(self.settings_build.os)
            raise ConanInvalidConfiguration(
                f"The build architecture '{self.settings_build.arch}' "
                f"is not supported for {self.settings_build.os}. "
                "Pre-compiled binaries are only available for "
                f"{supported_build_architectures[build_os]}."
            )

        # Validate version-variant compatibility
        if self.settings_target:
            variant = self._determine_llvm_variant()

            try:
                available_variants = list(
                    self.conan_data['sources'][self.version].keys())
                if variant not in available_variants:
                    target_arch = self.settings_target.get_safe('arch')
                    target_os = self.settings_target.get_safe('os')
                    raise ConanInvalidConfiguration(
                        f"Version {self.version} does not support the '{variant}' variant "
                        f"required for target {target_os}/{target_arch}. "
                        f"Available variants for {self.version}: {available_variants}. "
                        f"Hint: ARM Cortex-M targets require version 20.1.0."
                    )
            except KeyError:
                raise ConanInvalidConfiguration(
                    f"Version {self.version} is not defined in conandata.yml"
                )

    def build_requirements(self):
        if self.options.require_cmake:
            self.tool_requires("cmake/[>=3.28.0 <5.0.0]", visible=True)
        if self.options.require_ninja:
            self.tool_requires("ninja/[^1.0.0]", visible=True)

    def source(self):
        pass

    def build(self):
        pass

    def _determine_llvm_variant(self):
        """Determine which LLVM variant to download based on target architecture"""
        # The command for cross compiling this project for a particular binary,
        # in order to fetch the binaries for that version of LLVM use:
        #
        #      conan create all -pr:b default -pr:h hal/mcu/stm32f103c8 -pr:h hal/tc/llvm-20.1.0 --version=20.1.0 --build-require
        #
        # This will set the settings_target which will download the appropriate
        # fork of LLVM for that architecture.
        if not self.settings_target:
            self.output.info("Using upstream LLVM binary")
            return "upstream"

        TARGET_OS = self.settings_target.get_safe("os")
        TARGET_ARCH = self.settings_target.get_safe("arch")

        self.output.warning(
            f"TARGET_OS:{TARGET_OS}, TARGET_ARCH:{TARGET_ARCH}")

        # ARM Cortex-M baremetal gets special ARM Embedded Toolchain
        if TARGET_OS == "baremetal" and TARGET_ARCH in [
            "cortex-m0", "cortex-m0plus", "cortex-m1",
            "cortex-m3", "cortex-m4", "cortex-m4f",
            "cortex-m7", "cortex-m7f", "cortex-m7d",
            "cortex-m23", "cortex-m33", "cortex-m33f",
            "cortex-m35p", "cortex-m35pf",
            "cortex-m55", "cortex-m85",
        ]:
            self.output.info("Using ARM Embedded LLVM fork")
            return "arm-embedded"

        # Everything else uses regular LLVM
        # This includes:
        # - RISC-V (riscv32, riscv64)
        # - AVR (avr)
        # - Other ARM variants (cortex-a, etc.)
        # - Host builds
        self.output.info("Using upstream LLVM binary")
        return "upstream"

    def _extract_macos_dmg(self, url: str, sha256: str):
        # Download and store  to source folder just for storage
        LOCAL_DMG_FILE = Path(self.source_folder) / "llvm.dmg"
        download(self, url, LOCAL_DMG_FILE)

        # Mount the DMG file system onto the build folder
        subprocess.run(
            ["hdiutil", "attach", str(LOCAL_DMG_FILE), "-mountpoint",
             self.build_folder, "-nobrowse", "-readonly", "-quiet"])

        # Copy contents from LLVM directory to package folder
        PATHS = Path(self.build_folder).glob("LLVM-*")
        for path in PATHS:
            self.output.warning(f"📁 COPYING Contents of {path}")
            copy(self, "**", src=path, dst=self.package_folder, keep_path=True)
        # Copy contents from LLVM directory to package folder
        PATHS = Path(self.build_folder).glob("ATfE-*")
        for path in PATHS:
            self.output.warning(f"📁 COPYING Contents of {path}")
            copy(self, "**", src=path, dst=self.package_folder, keep_path=True)

        # Detach DMG
        subprocess.run(
            ["hdiutil", "detach", self.build_folder, "-force", "-quiet"])

        # Delete DMG file
        Path(LOCAL_DMG_FILE).unlink()

    def _extract(self, url: str, sha256: str):
        if url.endswith(".dmg"):
            self._extract_macos_dmg(url=url, sha256=sha256)
            return

        # Download and extract the LLVM binary package
        # All platforms use tar.xz archives now
        get(self, url, sha256=sha256, strip_root=True,
            destination=self.package_folder)

    def _download_and_install_clang_scan_deps(self,
                                              build_os: str,
                                              build_arch: str):
        CLANG_SCAN_DEPS_SHA256 = {
            "20": {
                "Linux_armv8": "3e92a5c676ddb28d48ef83a37147d031e8100f93c3f1394dd8fd9e3d868e61fd",
                "Linux_x86_64": "8a2b1d64982e3b73d19e283dc3baf1186a8a74634fa2ef72abeb980534fea3b6",
                "Macos_armv8": "14ad7609b9c89e7efd86337c67b89b2975e932ad183e88a21b4a26b19ae1b30c",
                "Macos_x86_64": "b450c31e94987fc0e3a0c568426f0726fdc0b3f10911ebc25e96984b3cf4f282",
                "Windows_armv8": "bf4cbaff98506e326f312a3da0fc4c345fc77055fd4cf8872de788d19d005430",
                "Windows_x86_64": "371c9e9140e63dacbd4e626a41c421e09e46fd17d3930b0d315072140ef0c6a9",
            }
        }

        LLVM_POLYFILL_URL_BASE = f"https://github.com/libhal/llvm-toolchain/releases/download/llvm-{self.version}-polyfill"
        BUILD = f"{build_os}_{build_arch}"
        URL = f"{LLVM_POLYFILL_URL_BASE}/{BUILD}-clang-scan-deps"

        if build_os == "Windows":
            FINAL_FILE_NAME = "clang-scan-deps.exe"
        else:
            FINAL_FILE_NAME = "clang-scan-deps"

        SCAN_DEPS_FILE_DESTINATION = Path(
            self.package_folder) / "bin" / FINAL_FILE_NAME
        download(self, URL,
                 sha256=CLANG_SCAN_DEPS_SHA256[self.version][BUILD],
                 filename=SCAN_DEPS_FILE_DESTINATION)
        chmod(self, SCAN_DEPS_FILE_DESTINATION, execute=True)

    def package(self):
        VARIANT = self._determine_llvm_variant()
        BUILD_OS = str(self.settings_build.os)
        BUILD_ARCH = str(self.settings_build.arch)

        self.output.info(f'VARIANT: {VARIANT}')
        self.output.info(f'BUILD_OS: {BUILD_OS}, BUILD_ARCH: {BUILD_ARCH}')

        URL = self.conan_data["sources"][self.version][VARIANT][BUILD_OS][BUILD_ARCH]["url"]
        SHA256 = self.conan_data["sources"][self.version][VARIANT][BUILD_OS][BUILD_ARCH]["sha256"]

        if VARIANT == "arm-embedded":
            # Download & install the missing `clang-scan-deps` from  ARM
            # toolchain (ARM's LLVM fork) does not include the binary. These
            # binaries were taken from the upstream LLVM project and added to this
            # directory.
            self._download_and_install_clang_scan_deps(BUILD_OS, BUILD_ARCH)
        self._extract(URL, SHA256)

    def setup_arm_cortex_m(self):
        # Configure CMake for cross-compilation
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_name", "Generic")
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_processor", "ARM")

        # Architecture-specific flags for ARM Cortex-M
        ARCH_MAP = {
            "cortex-m0": {
                "target": "armv6m-none-eabi",
                "cpu": "cortex-m0",
                "float_abi": "soft"
            },
            "cortex-m0plus": {
                "target": "armv6m-none-eabi",
                "cpu": "cortex-m0plus",
                "float_abi": "soft"
            },
            "cortex-m1": {
                "target": "armv6m-none-eabi",
                "cpu": "cortex-m1",
                "float_abi": "soft"
            },
            "cortex-m3": {
                "target": "armv7m-none-eabi",
                "cpu": "cortex-m3",
                "float_abi": "soft"
            },
            "cortex-m4": {
                "target": "armv7em-none-eabi",
                "cpu": "cortex-m4",
                "float_abi": "soft"
            },
            "cortex-m4f": {
                "target": "armv7em-none-eabihf",
                "cpu": "cortex-m4",
                "float_abi": "hard",
                "fpu": "fpv4-sp-d16"
            },
            "cortex-m7": {
                "target": "armv7em-none-eabi",
                "cpu": "cortex-m7",
                "float_abi": "soft"
            },
            "cortex-m7f": {
                "target": "armv7em-none-eabihf",
                "cpu": "cortex-m7",
                "float_abi": "hard",
                "fpu": "fpv5-sp-d16"
            },
            "cortex-m7d": {
                "target": "armv7em-none-eabihf",
                "cpu": "cortex-m7",
                "float_abi": "hard",
                "fpu": "fpv5-d16"
            },
            "cortex-m23": {
                "target": "armv8m.base-none-eabi",
                "cpu": "cortex-m23",
                "float_abi": "soft"
            },
            "cortex-m33": {
                "target": "armv8m.main-none-eabi",
                "cpu": "cortex-m33",
                "float_abi": "soft"
            },
            "cortex-m33f": {
                "target": "armv8m.main-none-eabihf",
                "cpu": "cortex-m33",
                "float_abi": "hard",
                "fpu": "fpv5-sp-d16"
            },
            "cortex-m35pf": {
                "target": "armv8m.main-none-eabihf",
                "cpu": "cortex-m35p",
                "float_abi": "hard",
                "fpu": "fpv5-sp-d16"
            },
            "cortex-m55": {
                "target": "armv8.1m.main-none-eabi",
                "cpu": "cortex-m55",
                "float_abi": "soft"
            },
            "cortex-m85": {
                "target": "armv8.1m.main-none-eabi",
                "cpu": "cortex-m85",
                "float_abi": "soft"
            },
        }

        c_flags = []
        cxx_flags = []
        exelinkflags = []
        definitions = [
            # LLVM's libc++ implementation needs a definition for the threads
            # API. Without this, the libc++ headers will emit a compile time
            # "error" stating that the thread API must be defined.
            "_LIBCPP_HAS_NO_THREADS=1"
        ]

        if self.options.default_linker_script:
            exelinkflags.append("-Wl,--default-script=picolibcpp.ld")

        if (self.options.default_arch and self.settings_target and
                self.settings_target.get_safe('arch') in ARCH_MAP):
            ARCH_CONFIG = ARCH_MAP[self.settings_target.get_safe('arch')]

            # Add target triple
            target_flag = f"-target {ARCH_CONFIG['target']}"
            c_flags.append(target_flag)
            cxx_flags.append(target_flag)
            exelinkflags.append(target_flag)

            # Add CPU specification
            cpu_flag = f"-mcpu={ARCH_CONFIG['cpu']}"
            c_flags.append(cpu_flag)
            cxx_flags.append(cpu_flag)
            exelinkflags.append(cpu_flag)

            # Add float ABI
            float_flag = f"-mfloat-abi={ARCH_CONFIG['float_abi']}"
            c_flags.append(float_flag)
            cxx_flags.append(float_flag)
            exelinkflags.append(float_flag)

            # Add FPU if specified
            if "fpu" in ARCH_CONFIG:
                fpu_flag = f"-mfpu={ARCH_CONFIG['fpu']}"
                c_flags.append(fpu_flag)
                cxx_flags.append(fpu_flag)
                exelinkflags.append(fpu_flag)

        if self.options.use_semihosting:
            SEMIHOST = ["-nostartfiles", "-lcrt0-semihost", "-lsemihost"]
            exelinkflags.extend(SEMIHOST)

        self.output.info(f'c_flags: {c_flags}')
        self.output.info(f'cxx_flags: {cxx_flags}')
        self.output.info(f'exelinkflags: {exelinkflags}')

        self.conf_info.append("tools.build:cflags", c_flags)
        self.conf_info.append("tools.build:cxxflags", cxx_flags)
        self.conf_info.append("tools.build:exelinkflags", exelinkflags)
        self.conf_info.append("tools.build:defines", definitions)

    @property
    def _lib_path(self) -> Path:
        return Path(self.package_folder) / "lib"

    def add_common_flags(self):
        c_flags = []
        cxx_flags = []
        exelinkflags = ["-fuse-ld=lld "]

        if self.options.lto:
            c_flags.append("-flto ")
            cxx_flags.append("-flto ")
            exelinkflags.append("-flto ")

        if self.options.function_sections:
            c_flags.append("-ffunction-sections ")
            cxx_flags.append("-ffunction-sections ")

        if self.options.data_sections:
            c_flags.append("-fdata-sections ")
            cxx_flags.append("-fdata-sections ")

        if self.options.gc_sections:
            if self.settings_target:
                if self.settings_target.get_safe("os") == "Macos":
                    exelinkflags.append("-Wl,-dead_strip ")
                elif self.settings_target.get_safe("os") != "Windows":
                    exelinkflags.append("-Wl,--gc-sections ")
                else:
                    pass
                    # LLVM will apply gc-sections automatically for Windows

        self.conf_info.append("tools.build:cflags", c_flags)
        self.conf_info.append("tools.build:cxxflags", cxx_flags)
        self.conf_info.append("tools.build:exelinkflags", exelinkflags)

    def setup_linux(self):
        self.cpp_info.libdirs = []

        library_path = ""
        if self.settings.arch == "x86_64":
            library_path = self._lib_path / "x86_64-unknown-linux-gnu"
        elif self.settings.arch == "armv8":
            library_path = self._lib_path / "aarch64-unknown-linux-gnu"

        EXELINKFLAGS = [
            f"-Wl,-rpath,{str(library_path)} "
            f"-L{str(library_path)} ",
            "-lc++ "
            "-lc++abi "
        ]

        for flag in EXELINKFLAGS:
            self.conf_info.append("tools.build:exelinkflags", flag)

    def setup_windows(self):
        # This may look a bit odd but the gnu:disable_flag instructs Conan
        # to ignore the host profile's libcxx settings with regards to the
        # generated conan_toolchain.cmake file.
        #
        # If this is removed, then building with this the `-std=libc++` flag
        # will result in a warning from the compiler about the argument being
        # unused.
        self.conf_info.append("tools.gnu:disable_flags", 'libcxx')

    def setup_mac_osx(self):
        # Disable Conan's automatic library directories
        self.cpp_info.libdirs = []

    def package_info(self):
        self.conf_info.define("tools.build:compiler_executables", {
            "c": "clang",
            "cpp": "clang++",
            "asm": "clang",
        })

        # Configure Ninja as CMake generator if required
        if self.options.require_ninja:
            self.conf_info.define(
                "tools.cmake.cmaketoolchain:generator", "Ninja")

        # Add CMake utility tools
        cmake_extra_variables = {
            "CMAKE_OBJCOPY": "llvm-objcopy",
            "CMAKE_SIZE_UTIL": "llvm-size",
            "CMAKE_OBJDUMP": "llvm-objdump",
            "CMAKE_AR": "llvm-ar",
            "CMAKE_RANLIB": "llvm-ranlib",
        }

        # Add C++ modules support if cmake and ninja are required
        if self.options.require_cmake and self.options.require_ninja:
            cmake_extra_variables["CMAKE_CXX_SCAN_FOR_MODULES"] = "ON"
            cmake_extra_variables["CMAKE_EXPERIMENTAL_EXPORT_PACKAGE_DEPENDENCIES"] = "1942b4fa-b2c5-4546-9385-83f254070067"

        self.conf_info.update(
            "tools.cmake.cmaketoolchain:extra_variables", cmake_extra_variables)

        self.buildenv_info.define("LLVM_INSTALL_DIR", self.package_folder)

        if self.settings_target:
            self.add_common_flags()
            if self.settings_target.get_safe('os') == 'Macos':
                self.setup_mac_osx()
            elif self.settings_target.get_safe('os') == 'Linux':
                self.setup_linux()
            elif self.settings_target.get_safe('os') == 'Windows':
                self.setup_windows()
            elif self.settings_target.get_safe('os') == 'baremetal':
                ARCH = str(self.settings_target.get_safe('arch'))
                if ARCH.startswith('cortex-m'):
                    self.setup_arm_cortex_m()

    def package_id(self):
        # All options should be removed as none of them should impact the
        # package id hash. These options are only used for delivering command
        # line arguments via the package_info.
        del self.info.options.default_arch
        del self.info.options.lto
        del self.info.options.function_sections
        del self.info.options.data_sections
        del self.info.options.gc_sections
        del self.info.options.require_cmake
        del self.info.options.require_ninja
        del self.info.options.use_semihosting
        # Remove any compiler or build_type settings from recipe hash
        del self.info.settings.compiler
        del self.info.settings.build_type

        # Normalize Cortex-M variants to share the same package_id
        if self.settings_target:
            target_arch = str(self.settings_target.get_safe("arch") or "")
            target_os = str(self.settings_target.get_safe("os") or "")

            # All Cortex-M variants use the SAME binary - normalize them
            if target_os == "baremetal" and target_arch.startswith("cortex-m"):
                # Use conf system to modify the hash for the package ID
                self.info.conf.define("user.llvm:target_family", "cortex-m")
