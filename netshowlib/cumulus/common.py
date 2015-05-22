# pylint: disable=E0611
# pylint: disable=W0403
# pylint: disable=W0612
""" Cumulus provider common module
"""
import re
from netshowlib.linux import common as linux_common


def is_phy(ifacename):
    """
    :returns: true if iface name is a physical port.
    Check only requires interface name
    """
    if re.match(r'swp\d+(s\d+)?$', ifacename):
        return True
    return False

def is_vlan_aware_bridge(ifacename):
    """
    used in :meth:`is_svi_initial_test`
    :params ifacename: interface name.
    :return: True if ``bridge/vlan_filtering`` exists and is set to 1
    """
    _vlanfiltering = linux_common.read_from_sys('bridge/vlan_filtering', ifacename)
    if _vlanfiltering and _vlanfiltering == "1":
        return True
    return False


