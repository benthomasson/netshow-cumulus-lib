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
    _vlanfiltering = linux_common.read_from_sys('bridge/vlan_filtering',
                                                ifacename)
    if _vlanfiltering and _vlanfiltering == "1":
        return True
    return False


def vlan_aware_vlan_list(ifacename, type_of_vlan):
    """
    :param type_of_vlan:  can be 'untagged_vlans' or 'vlans'
    :return: list of vlans supported on vlan aware physical/bond port
    """
    vlan_list = []
    attr_value = "brport/%s" % (type_of_vlan)
    bitmap_array = linux_common.read_from_sys(attr_value,
                                              ifacename, oneline=False)
    if bitmap_array:
        vlanid = 0
        for bit32entry in bitmap_array:
            hex32entry = re.sub('0x', '', bit32entry).strip()
            # convert hex entry to binary entry. Obtained from
            # Stackoverflow
            scale = 16
            num_of_bits = 32
            # converts hex string into binary string
            mod32bit = bin(int(hex32entry, scale))[2:].zfill(num_of_bits)
            # loop over the reverse of `range(32)` since vlans are listed
            # from left to right
            for i in reversed(range(32)):
                # If vlan bit is set to one, add it to the vlan list
                if mod32bit[i] == '1':
                    vlan_list.append(str(vlanid))
                # increment vlan after from the list when check is done
                vlanid += 1
    return vlan_list
