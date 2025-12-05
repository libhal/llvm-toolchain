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
from conan.tools.files import get, download, copy
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
        "lto": [True, False],
        "function_sections": [True, False],
        "data_sections": [True, False],
        "gc_sections": [True, False],
    }

    default_options = {
        "default_arch": True,
        "lto": True,
        "function_sections": True,
        "data_sections": True,
        "gc_sections": True,
    }

    options_description = {
        "default_arch": "Automatically inject architecture-appropriate -target and -mcpu arguments into compilation flags.",
        "lto": "Enable LTO support in binaries and intermediate files (.o and .a files)",
        "function_sections": "Enable -ffunction-sections which splits each function into their own subsection allowing link time garbage collection.",
        "data_sections": "Enable -fdata-sections which splits each statically defined block memory into their own subsection allowing link time garbage collection.",
        "gc_sections": "Enable garbage collection at link stage. Only useful if at least function_sections and data_sections is enabled."
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

    def source(self):
        pass

    def build(self):
        pass

    def _determine_llvm_variant(self):
        """Determine which LLVM variant to download based on target architecture"""

        # If no cross-compilation, use regular LLVM
        if not self.settings_target:
            self.output.warning("settings target does not exist??")
            return "host"

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
            return "arm-embedded"

        # Everything else uses regular LLVM
        # This includes:
        # - RISC-V (riscv32, riscv64)
        # - AVR (avr)
        # - Other ARM variants (cortex-a, etc.)
        # - Host builds
        return "host"

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

    def package(self):
        VARIANT = self._determine_llvm_variant()
        BUILD_OS = str(self.settings_build.os)
        BUILD_ARCH = str(self.settings_build.arch)

        self.output.info(
            f'VARIANT: {VARIANT}, BUILD_OS: {BUILD_OS}, BUILD_ARCH: {BUILD_ARCH}')
        try:
            URL = self.conan_data["sources"][self.version][VARIANT][BUILD_OS][BUILD_ARCH]["url"]
            SHA256 = self.conan_data["sources"][self.version][VARIANT][BUILD_OS][BUILD_ARCH]["sha256"]

            self._extract(URL, SHA256)
        except KeyError:
            raise ConanInvalidConfiguration(
                f"Binary package for LLVM {self.version} not available for {BUILD_OS}/{BUILD_ARCH}")

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
            if self.settings_target.os == "Macos":
                exelinkflags.append("-Wl,-dead_strip ")
            elif self.settings_target.os != "Windows":
                exelinkflags.append("-Wl,--gc-sections ")
            else:
                pass  # LLVM will apply gc-sections automatically for Windows

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

        # Add CMake utility tools
        self.conf_info.update("tools.cmake.cmaketoolchain:extra_variables", {
            "CMAKE_OBJCOPY": "llvm-objcopy",
            "CMAKE_SIZE_UTIL": "llvm-size",
            "CMAKE_OBJDUMP": "llvm-objdump",
            "CMAKE_AR": "llvm-ar",
            "CMAKE_RANLIB": "llvm-ranlib",
        })

        self.buildenv_info.define("LLVM_INSTALL_DIR", self.package_folder)

        # ADD THIS: Call ARM setup when cross-compiling to ARM
        if self.settings_target and self.settings_target.get_safe('os') == 'baremetal':
            self.setup_arm_cortex_m()

        self.add_common_flags()
        if self.settings_build.os == "Macos":
            self.setup_mac_osx()
        if self.settings_build.os == "Linux":
            self.setup_linux()
        if self.settings_build.os == "Windows":
            self.setup_windows()

    def package_id(self):
        # All options should be removed as none of them should impact the
        # package id hash. These options are only used for delivering command
        # line arguments via the package_info.
        del self.info.options.default_arch
        del self.info.options.lto
        del self.info.options.function_sections
        del self.info.options.data_sections
        del self.info.options.gc_sections
        # Remove any compiler or build_type settings from recipe hash
        del self.info.settings.compiler
        del self.info.settings.build_type
