import os

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # For cross-compilation toolchains, we just verify the binary was created
        # We cannot run ARM binaries on x86/ARM macOS/Linux/Windows hosts
        if cross_building(self):
            self.output.info(
                "Cross-compilation successful! Binary created for target architecture.")
            binary_path = os.path.join(
                self.cpp.build.bindirs[0], "test_package")
            if not os.path.exists(binary_path):
                raise Exception(f"Expected binary not found at: {binary_path}")
            self.output.success(f"Test binary exists at: {binary_path}")
        else:
            bin_path = os.path.join(self.cpp.build.bindirs[0], "test_package")
            self.run(bin_path, env="conanrun")
