from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.build import cross_building
from pathlib import Path


class Demo(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"

    def build_requirements(self):
        self.tool_requires("cmake/4.1.2")

    def requirements(self):
        pass

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # For cross-compilation toolchains, we just verify the binary was created
        # We cannot run ARM binaries on x86/ARM macOS/Linux/Windows hosts
        BINARY_PATH = Path(self.cpp.build.bindirs[0]) / "demo"
        if not BINARY_PATH.exists():
            raise Exception(f"Expected binary not found at: {BINARY_PATH}")
        if cross_building(self):
            self.output.info(
                "Cross-compilation successful! Binary created for target architecture.")
            self.output.success(f"Test binary exists at: {BINARY_PATH}")
        else:
            self.run(str(BINARY_PATH), env="conanrun")
