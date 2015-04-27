"""
This modules run a Provider discovery check for Cumulus
"""

try:
    import netshowlib.linux.common as common_mod
except ImportError:
    common_mod = None


def check():
    """
    Cumulus Provider Check
    :return: name of OS found if check is true
    """

    # if netshowlib.linux.common module is not found..return None
    if not common_mod:
        return None
    try:
        _distro_info = common_mod.distro_info()
        vendor_name = _distro_info.get('ID')
        if vendor_name and vendor_name.lower() == 'cumulus networks':
            return 'cumulus'
    except common_mod.ExecCommandException:
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
