from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
from conans.tools import os_info, SystemPackageTool
import os

 
class OathtoolkitConan(ConanFile):
    name = "oath-toolkit"
    version = "2.6.2"
    license = "<Put the package license here>"
    url = "https://www.nongnu.org/oath-toolkit/"
    description = "The OATH Toolkit provide components for building one-time password authentication systems."
    settings = "os", "compiler", "build_type", "arch"
    options = {"liboath": [True, False],
               "libpskc": [True, False],
                "tools": [True, False],
               }
    default_options = '''
liboath=True
libpskc=True
tools=True
'''

    exports_sources = "oath-toolkit-2.6.2-fix-build-with-gcc7.patch"

    def configure(self):
        if self.settings.os != "Linux" or os_info.linux_distro != "ubuntu":
            self.output.warn("Tested only in Linux Ubuntu!")

    def source_folder_name(self):
        return "oath-toolkit-%s" % self.version

    def source(self):
        source_folder_name = self.source_folder_name()
        targz_name = "%s.tar.gz" % source_folder_name
        link_download = "http://download.savannah.nongnu.org/releases/oath-toolkit/%s" % (targz_name)
        tools.download(link_download, targz_name) 
        tools.untargz(targz_name, ".")
        os.unlink(targz_name)

    def buildWithAutoTools(self, buildFolder):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.configure(configure_dir=buildFolder)
        env_build.make()


    def build(self):
        source_folder_name = self.source_folder_name()
        if self.settings.compiler.version >= 7: #Fixing bug gcc 7 ==> https://bugs.gentoo.org/618100 <==
            self.run("patch --batch %s/%s/gl/intprops.h < oath-toolkit-2.6.2-fix-build-with-gcc7.patch" % (source_folder_name, "pskctool"))
            self.run("patch --batch %s/%s/gl/intprops.h < oath-toolkit-2.6.2-fix-build-with-gcc7.patch" % (source_folder_name, "libpskc"))
            self.run("patch --batch %s/%s/gl/intprops.h < oath-toolkit-2.6.2-fix-build-with-gcc7.patch" % (source_folder_name, "oathtool"))

        if self.options.liboath:
            self.buildWithAutoTools(buildFolder="%s/liboath" % (source_folder_name))
        if self.options.libpskc:
            self.buildWithAutoTools(buildFolder="%s/libpskc" % (source_folder_name))
        if self.options.tools:
           self.buildWithAutoTools(buildFolder="%s" % (source_folder_name))

    def system_requirements(self):
        installer = SystemPackageTool() # tested only in Linux Ubuntu.
        installer.install("libxml2-dev", update=False)
        installer.install("libxml2-utils", update=False)
        installer.install("libxmlsec1-dev", update=False)

    def package(self):
        source_folder_name = self.source_folder_name()
        if self.options.liboath:
            self.copy("oath.h", dst="include" , src="%s/liboath" % source_folder_name, keep_path=False)
            self.copy("liboath.so*", dst="lib", src=".libs", keep_path=False, links=True)
            self.copy("liboath.a", dst="lib", src=".libs", keep_path=False)
        if self.options.libpskc:
            self.copy("pskc.h", dst="include" , src="%s/libpskc/include/pskc" % source_folder_name, keep_path=False)
            self.copy("libpskc.so*", dst="lib", src=".libs", keep_path=False, links=True)
            self.copy("libpskc.a", dst="lib", src=".libs", keep_path=False)
        if self.options.tools:
            self.copy("oathtool", src="oathtool", dst="bin", keep_path=False)
            self.copy("pskctool", src="pskctool", dst="bin", keep_path=False)

    def deploy(self):
        self.copy("oathtool", src="bin", keep_path=False)
        self.copy("pskctool", src="bin", keep_path=False)

    def package_info(self):
        if self.options.liboath:
            self.cpp_info.libs.append("oath")
        if self.options.libpskc:
            self.cpp_info.libs.append("pskc")

