#!/usr/bin/env python

"""
gitutils.py - provide integration with git

Provide integration with git such as:
- list_files  - lists all files tracked by the repo
- get_version - get the most recent version from a git tag

Original idea for listing files tracked by git was, setuptools-git
package found at:
    http://pypi.python.org/pypi/setuptools-git

Original idea for generating the version from a git tag was taken from:
    http://dcreager.net/2010/02/10/setuptools-git-version-numbers/
    -and-
    https://gist.github.com/2567778

WARNING: All functions within this module depend on the git package
being installed and accessable via the PATH environment variable.

-----------

Copyright (C) 2012, Jonathan Toppins <jtoppins@users.sourceforge.net>
All Rights Reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Jonathan Toppins BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Inspiration and code for which these ideas were copied from exist under
Public Domain licenses.
"""

#--------------------------------------------------------------------
# Internal stuff
#

__all__ = ("list_files", "get_version")

import string
import locale
import subprocess


#--------------------------------------------------------------------
# Internal variables & support functions
#

ENCODING = locale.getpreferredencoding()

def _read_release_version(filename):
    """
    return the version number stored in the file specified by filename
    """
    try:
        f = open(filename, "r")
        try:
            version = f.readline()
            return version.strip().decode(ENCODING)
        finally:
            f.close()
    except:
        return None

def _write_release_version(filename, version):
    """
    write the version string to the file filename
    """
    f = open(filename, "w")
    f.write(u"%s\n" % version.encode(ENCODING))
    f.close()

def _call_git_describe(abbrev=7):
    """
    call_git_describe([abbrev])
    Calls git-describe, if abbrev is provided it is passed as the value
    to the '--abbrev' option, see man git-describe for details
    """
    try:
        _p = subprocess.Popen(['git', 'describe', '--tags', '--abbrev=%d' % abbrev],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _p.stderr.close()
        line = _p.stdout.readlines()[0]
        _p.wait()
        return line.strip().decode(ENCODING)
    except:
        # ignore all errors
        return None

def _pep386adapt(version):
    """
    Adapt git-describe version to be in line with PEP 386.
    """
    if None != version:
        prefix = string.ascii_letters
        parts = version.split(u'-')
        parts[-2] = 'dev'+parts[-2]
        version = '.'.join(parts[:-1])
        version = version.lstrip(prefix)
    return version

#--------------------------------------------------------------------
# Public functions
#

def list_files(dirname=""):
    """
    list_files([dirname])

    List files tracked by a git repository. If dirname is provided all
    files within that subtree of the repository will be listed.

    On error this function will raise an exception
    """
    p = subprocess.Popen(['git', 'ls-files', dirname],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.stderr.close()
    files = p.stdout.readlines()
    p.wait()
    return [f.strip().decode(ENCODING) for f in files]

def get_version(abbrev=0, filename="RELEASE-VERSION".encode(ENCODING)):
    """
    get_version([abbrev])

    Get latest version number of the code, either from the repository or
    from a file stored in the source distribution. Prefer the repository
    generated version over the version stored in the file and if the
    one stored in the file doesn't equal the generated one, update the file.

    abbrev - a number passed directly to the '--abbrev' of git-describe
    filename - the filename to look in if git-describe fails

    Detailed Description:
    Calculates the current version number.  If possible, this is the
    output of "git describe", modified to conform with the versioning
    scheme specified in PEP389.  If "git describe" returns an error
    (most likely because we're in an unpacked copy of a release tarball,
    rather than in a git working copy), then we fall back on reading the
    contents of the RELEASE-VERSION file.

    This will automatically update the RELEASE-VERSION file, if
    necessary.  Note that the RELEASE-VERSION file should *not* be
    checked into git; please add it to your top-level .gitignore file.

    You'll probably want to distribute the RELEASE-VERSION file in your
    sdist tarballs; to do this, just create a MANIFEST.in file that
    contains the following line:
        include RELEASE-VERSION

    Original author: Douglas Creager <dcreager@dcreager.net>
    """

    release_version = _read_release_version(filename)
    version = _call_git_describe(abbrev)

    if version is None:
        version = release_version
    if version is None:
        raise ValueError("Cannot find the version number!")
    if version != release_version:
        _write_release_version(filename, version)
    return version

if __name__ == "__main__":
    from pprint import pprint

    pprint(list_files("."))
    print("Version: ", get_version())
