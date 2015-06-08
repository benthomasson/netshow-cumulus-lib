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
from setuptools import setup, find_packages

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
        # not sure why this is only required for stdeb..
        # when doing python setup.py bdist_wheel it just grabs the mo files
        # from build with no issues.
        if isinstance(self.root, str) and os.environ.get('DEB_BUILD_GNU_SYSTEM'):
            _dest = os.path.join(self.install_dir, 'share', 'locale')
            _src = '../../build/mo'
            try:
                log.info("copying files from %s to %s" % (_src, _dest))
                shutil.copytree(_src, _dest)
            except shutil.Error as _exception:
                log.info("Directory failed to copy. Error: %s" % _exception)
            except OSError as _exception:
                log.info("Directory failed to copy. Error: %s" % _exception)

setup(
    name='netshow-cumulus-lib',
    version=get_version(),
    description="Cumulus Linux Provider for Netshow - Linux Network Abstraction Library",
    author='Cumulus Networks',
    author_email='ce-ceng@cumulusnetworks.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license='To Be Announced',
    cmdclass={"install_data": PostInstall,
              "build": BuildWithI18n},
    namespace_packages=['netshowlib', 'netshowlib.cumulus',
                        'netshow', 'netshow.cumulus'],
    install_requires=[
        'netshow-lib',
        'netshow',
        'docopt',
        'tabulate',
        'inflection',
        'netshow-linux-lib'
    ],
    classifiers=[
        'Topic :: System :: Networking',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX :: Linux'
    ],
    data_files=[('share/netshow-lib/providers', ['data/provider/cumulus'])],
    use_2to3=True
)
