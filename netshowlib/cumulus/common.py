# pylint: disable=E0611
# pylint: disable=W0403
# pylint: disable=W0612
""" Cumulus provider common module
"""
import re


def is_phy(ifacename):
    """
    :returns: true if iface name is a physical port.
    Check only requires interface name
    """
    if re.match(r'swp\d+(s\d+)?$', ifacename):
        return True
    return False
