from pathlib import Path
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeToolchain, CMakeDeps
from conan.tools.build import cross_building


class TestPackageConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)
        self.tool_requires("cmake/[>=3.28.0 <5.0.0]")
        self.tool_requires("make/4.4.1")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generator = "Unix Makefiles"
        tc.generate()
        if self.settings.os == "Windows":
            tc.cache_variables["CMAKE_MSVC_RUNTIME_LIBRARY"] = ""

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        self.output.info(f"build_folder: {self.build_folder}")
        self.output.info(f"cpp.build.bindirs: {self.cpp.build.bindirs}")

        BINARY_PATH = Path(self.build_folder) / \
            self.cpp.build.bindirs[0] / "test_package"

        self.output.info(f"BINARY_PATH: {BINARY_PATH}")
        if not BINARY_PATH.exists():
            raise Exception(f"Expected binary not found at: {BINARY_PATH}")

        self.output.info(f"Test binary exists at: {BINARY_PATH}")
        if cross_building(self):
            self.output.success(
                "Cross-compilation successful! Binary created for target architecture!")
        else:
            self.run(str(BINARY_PATH), env="conanrun")
