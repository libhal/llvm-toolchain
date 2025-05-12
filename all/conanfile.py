import os
import platform
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
        os_name = str(self.settings.os)
        arch_name = str(self.settings.arch)

        try:
            url = self.conan_data["sources"][self.version][os_name][arch_name]["url"]
            sha256 = self.conan_data["sources"][self.version][os_name][arch_name]["sha256"]
        except KeyError:
            raise ConanInvalidConfiguration(
                f"Binary package for LLVM {self.version} not available for {os_name}/{arch_name}")

        # For Windows, the download might be an installer, so special handling needed
        if self.settings.os == "Windows":
            filename = os.path.basename(url)
            download(self, url, filename, sha256=sha256)
            # For Windows, we'll extract the installer contents in the package step
        else:
            # For Linux/Mac, we can directly extract the tarball
            get(self, url, sha256=sha256, strip_root=True)

    def package(self):
        if self.settings.os == "Windows":
            # For Windows, we'd need to extract from the installer
            # This is a simplified approach - in practice, you might need a more complex extraction
            # Consider using 7z or similar to extract contents from the exe
            self.output.warn(
                "Windows packaging may need special handling for extracting from installers")

            # Copy any relevant files that were downloaded or extracted
            copy(self, "*.exe", self.source_folder,
                 os.path.join(self.package_folder, "bin"))
            copy(self, "*.dll", self.source_folder,
                 os.path.join(self.package_folder, "bin"))
            copy(self, "*.lib", self.source_folder,
                 os.path.join(self.package_folder, "lib"))
            copy(self, "*.h", self.source_folder,
                 os.path.join(self.package_folder, "include"))

            resource_dir = os.path.join(self.package_folder, "res/")
            copy(self, pattern="toolchain.cmake", src=self.build_folder,
                 dst=resource_dir, keep_path=True)
        else:
            # For Linux/Mac, just copy all contents from the extracted tarball
            copy(self, "*", self.source_folder, self.package_folder)

            resource_dir = os.path.join(self.package_folder, "res/")
            copy(self, pattern="toolchain.cmake", src=self.build_folder,
                 dst=resource_dir, keep_path=True)

    def package_info(self):
        # Add binaries to path
        bin_path = os.path.join(self.package_folder, "bin")
        self.buildenv_info.append_path("PATH", bin_path)

        # Add library path for runtime dependencies
        lib_path = os.path.join(self.package_folder, "lib")
        if platform.system() == "Darwin":
            self.buildenv_info.append_path("DYLD_LIBRARY_PATH", lib_path)
        else:
            self.buildenv_info.append_path("LD_LIBRARY_PATH", lib_path)

        # Set environment variables that might be useful for tools using this toolchain
        self.buildenv_info.define("LLVM_INSTALL_DIR", self.package_folder)
        self.buildenv_info.define("LLVM_VERSION", self.version)

        # Make the CMake toolchain file available
        f = os.path.join(self.package_folder, "res/toolchain.cmake")
        self.conf_info.append("tools.cmake.cmaketoolchain:user_toolchain", f)

        # If there's a cmake directory with config files, add it to CMAKE_PREFIX_PATH
        if os.path.exists(os.path.join(self.package_folder, "lib", "cmake", "llvm")):
            cmake_path = os.path.join(self.package_folder, "lib", "cmake")
            self.buildenv_info.append_path("CMAKE_PREFIX_PATH", cmake_path)
