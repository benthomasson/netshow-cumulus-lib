"""
This modules run a Provider discovery check for Cumulus
"""

try:
    import netshowlib.linux.common as common_mod
except ImportError:
    common_mod = None
import re


def check():
    """
    Cumulus Provider Check
    :return: name of OS found if check is true
    """

    # if netshowlib.linux.common module is not found..return None
    if not common_mod:
        return None
    try:
        _distro_info = open('/etc/lsb-release', 'r').readlines()
        for _line in _distro_info:
            if _line.startswith('DISTRIB_ID'):
                vendor_name = _line.split('=')[1]
        if vendor_name and re.search('cumulus', vendor_name.lower()):
            return 'cumulus'
    except IOError:
        return None
    return None


def name_and_priority():
    """
    name and priority for Cumulus provider
    name = Cumulus
    priority = 1. Lower priority means less likely candidate
    """
    os_name = check()
    if os_name:
        return {os_name: '1'}
    return None
