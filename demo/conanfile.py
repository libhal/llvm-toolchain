from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout
from conan.errors import ConanInvalidConfiguration


class Demo(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "CMakeDeps", "CMakeToolchain", "VirtualBuildEnv"

    @property
    def _compiler_version(self):
        SUPPORTED_COMPILER_VERSIONS = ["19.1.7"]

        if self.settings.compiler.version not in SUPPORTED_COMPILER_VERSIONS:
            raise ConanInvalidConfiguration(
                "The GCC compiler version must be one of these " +
                f"{SUPPORTED_COMPILER_VERSIONS}, provided version: " +
                f"'{self.settings.compiler.version}'")

        return str(self.settings.compiler.version)

    def validate(self):
        if self.settings.compiler != "clang":
            raise ConanInvalidConfiguration(
                "This demo requires the compiler to be clang, provided: " +
                f"'{self.settings.compiler}'")

    def build_requirements(self):
        self.tool_requires("cmake/3.27.1")

    def requirements(self):
        pass

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
