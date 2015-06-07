# pylint: disable=c0111

from netshowlib.cumulus._version import get_version
import os
import shutil
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass
from distutils.command.install_data import install_data
from distutils.command.build import build
from distutils import log


class BuildWithI18n(build):
    sub_commands = build.sub_commands + [('build_i18n', None)]

    def run(self):
        build.run(self)


class PostInstall(install_data):
    def run(self):
        # run through the regular install data
        # now install the translation stuff
        # run "setup.py build_i18n -m" first first before executing

        install_data.run(self)

from setuptools import setup, find_packages
setup(
    name='netshow-cumulus-lib',
    version=get_version(),
    url="http://github.com/CumulusNetworks/netshow-lib",
    description="Python Library to Abstract Linux Networking Data",
    author='Cumulus Networks',
    author_email='ce-ceng@cumulusnetworks.com',
    packages=find_packages(),
    zip_safe=False,
    license='GPLv2',
    cmdclass={"install_data": PostInstall,
              "build": BuildWithI18n},
    namespace_packages=['netshowlib', 'netshowlib.cumulus'],
    install_requires=[
        'netshow',
        'netshow-lib',
        'docopt',
        'tabulate',
        'flufl.i18n',
        'netshow-linux-lib'
    ],
    use_2to3=True,
    classifiers=[
        'Topic :: System :: Networking',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux'
    ],
    data_files=[('share/netshow-lib/providers', ['data/provider/cumulus'])]
)
