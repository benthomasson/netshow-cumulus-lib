"""
Bridge module for the cumulus provider
"""

from netshowlib.cumulus import common
from netshowlib.linux import bridge as linux_bridge
from netshowlib.cumulus import mstpd
import re


class MstpctlStpBridge(object):
    """
    class responsible to managing stp info gathered from mstpctl
    """
    def __init__(self, bridge, cache):
        self.bridge = bridge
        self._root_priority = None
        self._bridge_priority = None
        if cache:
            self.cache = cache.get('mstpd').get('bridge')
        else:
            self.cache = mstpd.cacheinfo().get('bridge')
        self._stpdetails = self.cache.get(self.bridge.name)

    def is_root(self):
        """
        :return: True if switch is root for bridge domain
        """
        return self._stpdetails.get('designated_root') == \
            self._stpdetails.get('bridge_id')

    @property
    def root_priority(self):
        """
        :return root priority
        """
        return int(self._stpdetails.get('designated_root').split('.')[0]) * 4096

    @property
    def bridge_priority(self):
        """
        :return: bridge priority
        """
        return int(self._stpdetails.get('bridge_id').split('.')[0]) * 4096

    @property
    def member_state(self):
        """
        :return: stp state of iface members of the bridge
        """
        return self._stpdetails.get('ifaces')


class BridgeMember(linux_bridge.BridgeMember):
    """
    Class responsible for cumulus bridge member that is not a bond
    """

    @property
    def stp(self):
        """
        :return: ``None`` if STP is disabled
        :return: :class:`KernelStpBridge` instance if stp_state == 1
        :return: :class:`MstpctlStpBridge` instance if stp_state == 2
        """
        if self.read_from_sys('bridge/stp_state') == '2':
            self._stp = MstpctlStpBridge(self, self._cache)
            return self._stp
        return super(BridgeMember, self).stp


    @property
    def vlan_filtering(self):
        """
        :return: Determines if port is vlan aware or not
        """
        if self.read_from_sys('brport/vlans'):
            return True
        return False

    @property
    def vlan_list(self):
        """
        :return: list of vlans include native vlan if vlan aware
        :return: list of all tagged vlans if using classic driver
        """
        if self.vlan_filtering:
            return self.vlan_aware_vlan_list('vlans')
        else:
            return super(Bridge, self).vlan_list

    def vlan_aware_vlan_list(self, type_of_vlan):
        """
        :param type_of_vlan:  can be 'untagged_vlans' or 'vlans'
        :return: list of vlans supported on vlan aware physical/bond port
        TODO: move to common.py because used by bond and phy bridgemem
        """
        vlan_list = []
        attr_value = "brport/%s" % (type_of_vlan)
        bitmap_array = self.read_from_sys(attr_value)
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
                        vlan_list.append(vlanid)
                    # increment vlan after from the list when check is done
                    vlanid += 1
        return vlan_list


class Bridge(linux_bridge.Bridge):
    """ Bridge class for the cumulus provider
    """
    def __init__(self, name, cache=None):
        linux_bridge.Bridge.__init__(self, name, cache)
        self._vlan_filtering = 0

    @property
    def vlan_filtering(self):
        """
        :return the vlan filtering setting. If set to 1 trunk config is placed
         under the physical port and can be seen using bridge vlan show command
        """
        self._vlan_filtering = 0
        if common.is_vlan_aware_bridge(self.name):
            self._vlan_filtering = 1
        return self._vlan_filtering

    @property
    def stp(self):
        """
        :return: ``None`` if STP is disabled
        :return: :class:`KernelStpBridge` instance if stp_state == 1
        :return: :class:`MstpctlStpBridge` instance if stp_state == 2
        """
        if self.read_from_sys('bridge/stp_state') == '2':
            self._stp = MstpctlStpBridge(self, self._cache)
            return self._stp
        return super(Bridge, self).stp

    @property
    def members(self):
        """
        :return: list of bridge port members
        """
        self._get_members(BridgeMember)
        return self._members
