import os
import platform
from pathlib import Path
from conan import ConanFile
from conan.tools.files import get, copy, download, rmdir, save
from conan.errors import ConanInvalidConfiguration


class LLVMToolchainPackage(ConanFile):
    name = "llvm-toolchain"
    license = "Apache-2.0 WITH LLVM-exception"
    homepage = "https://releases.llvm.org/"
    description = "LLVM Toolchain for cross-compilation targeting various architectures"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "application"
    exports_sources = "toolchain.cmake"
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

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def validate(self):
        supported_build_operating_systems = ["Linux", "Macos", "Windows"]
        if not self._settings_build.os in supported_build_operating_systems:
            raise ConanInvalidConfiguration(
                f"The build os '{self._settings_build.os}' is not supported. "
                "Pre-compiled binaries are only available for "
                f"{supported_build_operating_systems}."
            )

        supported_build_architectures = {
            "Linux": ["armv8", "x86_64"],
            "Macos": ["armv8", "x86_64"],
            "Windows": ["x86_64"],
        }

        if (
            not self._settings_build.arch
            in supported_build_architectures[str(self._settings_build.os)]
        ):
            build_os = str(self._settings_build.os)
            raise ConanInvalidConfiguration(
                f"The build architecture '{self._settings_build.arch}' "
                f"is not supported for {self._settings_build.os}. "
                "Pre-compiled binaries are only available for "
                f"{supported_build_architectures[build_os]}."
            )

    def source(self):
        pass

    def build(self):
        # Get download URL and hash from conandata.yml based on version, OS and arch
        os_name = str(self._settings_build.os)
        arch_name = str(self._settings_build.arch)

        try:
            url = self.conan_data["sources"][self.version][os_name][arch_name]["url"]
            sha256 = self.conan_data["sources"][self.version][os_name][arch_name]["sha256"]
        except KeyError:
            raise ConanInvalidConfiguration(
                f"Binary package for LLVM {self.version} not available for {os_name}/{arch_name}")

        # Download and extract the LLVM binary package
        # All platforms use tar.xz archives now
        get(self, url, sha256=sha256, strip_root=True,
            destination=self.build_folder)

    def package(self):
        # Copy all LLVM files from build to package folder
        copy(self, "*", src=self.build_folder,
             dst=self.package_folder, keep_path=True)

        # Copy the CMake toolchain file to resources directory
        resource_dir = os.path.join(self.package_folder, "res")
        copy(self, "toolchain.cmake", src=self.source_folder,
             dst=resource_dir, keep_path=False)

    def add_common_flags(self):
        c_flags = []
        cxx_flags = []
        exelinkflags = []

        if self.options.lto:
            c_flags.append("-flto")
            cxx_flags.append("-flto")
            exelinkflags.append("-flto")

        if self.options.function_sections:
            c_flags.append("-ffunction-sections")
            cxx_flags.append("-ffunction-sections")

        if self.options.data_sections:
            c_flags.append("-fdata-sections")
            cxx_flags.append("-fdata-sections")

        self.conf_info.append("tools.build:cflags", c_flags)
        self.conf_info.append("tools.build:cxxflags", cxx_flags)
        self.conf_info.append("tools.build:exelinkflags", exelinkflags)

    def setup_arm_cortex_m(self):
        # Configure CMake for cross-compilation
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_name", "Generic")
        self.conf_info.define(
            "tools.cmake.cmaketoolchain:system_processor", "ARM")

        # Make the CMake toolchain file available
        toolchain_file = Path(self.package_folder) / "res" / "toolchain.cmake"
        self.conf_info.append(
            "tools.cmake.cmaketoolchain:user_toolchain", toolchain_file)
        self.output.info(f"Toolchain file: {toolchain_file}")

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

        if (self.options.default_arch and self.settings_target and
                self.settings_target.get_safe('arch') in ARCH_MAP):
            arch_config = ARCH_MAP[self.settings_target.get_safe('arch')]

            # Add target triple
            target_flag = f"-target {arch_config['target']}"
            c_flags.append(target_flag)
            cxx_flags.append(target_flag)
            exelinkflags.append(target_flag)

            # Add CPU specification
            cpu_flag = f"-mcpu={arch_config['cpu']}"
            c_flags.append(cpu_flag)
            cxx_flags.append(cpu_flag)
            exelinkflags.append(cpu_flag)

            # Add float ABI
            float_flag = f"-mfloat-abi={arch_config['float_abi']}"
            c_flags.append(float_flag)
            cxx_flags.append(float_flag)
            exelinkflags.append(float_flag)

            # Add FPU if specified
            if "fpu" in arch_config:
                fpu_flag = f"-mfpu={arch_config['fpu']}"
                c_flags.append(fpu_flag)
                cxx_flags.append(fpu_flag)
                exelinkflags.append(fpu_flag)

        self.output.info(f'c_flags: {c_flags}')
        self.output.info(f'cxx_flags: {cxx_flags}')
        self.output.info(f'exelinkflags: {exelinkflags}')

        self.conf_info.append("tools.build:cflags", c_flags)
        self.conf_info.append("tools.build:cxxflags", cxx_flags)
        self.conf_info.append("tools.build:exelinkflags", exelinkflags)

    def setup_mac_osx(self):
        import subprocess
        try:
            self.cpp_info.libdirs = []
            sdk_path = subprocess.check_output(["xcrun", "--show-sdk-path"],
                                               stderr=subprocess.STDOUT).decode().strip()
            INCLUDE_SYS_ROOT = [f"-isysroot {sdk_path}"]
            self.conf_info.append("tools.build:cflags", INCLUDE_SYS_ROOT)
            self.conf_info.append("tools.build:cxxflags", INCLUDE_SYS_ROOT)
            self.conf_info.append("tools.build:exelinkflags", INCLUDE_SYS_ROOT)
            self.conf_info.append(
                "tools.build:sharedlinkflags", INCLUDE_SYS_ROOT)
            self.output.info(f"INCLUDE_SYS_ROOT:{INCLUDE_SYS_ROOT}")
            if self.options.gc_sections:
                self.conf_info.append(
                    "tools.build:exelinkflags", ["-Wl,-dead_strip"])
        except Exception as e:
            self.output.warn(f"Could not determine macOS SDK path: {e}")

    def package_info(self):
        self.conf_info.define("tools.build:compiler_executables", {
            "c": "clang",
            "cpp": "clang++",
            "asm": "clang",
        })
        self.buildenv_info.define("LLVM_INSTALL_DIR", self.package_folder)
        self.add_common_flags()
        if self.settings.os == "Macos":
            self.setup_mac_osx()

    def package_id(self):
        del self.info.options.default_arch
        del self.info.options.lto
        del self.info.options.function_sections
        del self.info.options.data_sections
        del self.info.options.gc_sections
