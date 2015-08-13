# pylint: disable=c0111
# if installing this package from git, make sure to include 'gitversion'
# in requirements.txt
from gitversion import rewritable_git_version
import io
import os
try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass
from distutils.command.build import build
from setuptools import setup, find_packages


def read_contents(fname='README'):
    """read contents of readme into setup.py long_description field
    """
    return io.open(os.path.join(os.path.dirname(__file__),
                                fname), encoding="utf-8").read()


class BuildWithI18n(build):
    sub_commands = build.sub_commands + [('build_i18n', None)]

    def run(self):
        build.run(self)


setup(
    name='netshow-cumulus-lib',
    version=rewritable_git_version(__file__),
    description="Cumulus Linux Provider for Netshow - Network Abstraction and Aggregation Software",
    long_description=read_contents(),
    url='http://github.com/CumulusNetworks/netshow-cumulus-lib',
    author='Cumulus Networks',
    author_email='ce-ceng@cumulusnetworks.com',
    packages=find_packages(),
    zip_safe=False,
    license='GPLv2',
    cmdclass={"build": BuildWithI18n},
    namespace_packages=['netshowlib', 'netshowlib.cumulus',
                        'netshow', 'netshow.cumulus'],
    install_requires=[
        'netshow-core-lib',
        'netshow-core',
        'network-docopt',
        'tabulate',
        'inflection',
        'netshow-linux-lib',
        'cumulus-platform-info'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: System :: Networking',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux'
    ],
    data_files=[('share/netshow-lib/providers', ['data/provider/cumulus'])],
)
