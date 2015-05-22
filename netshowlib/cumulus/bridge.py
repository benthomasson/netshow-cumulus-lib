"""
Bridge module for the cumulus provider
"""

from netshowlib.cumulus import common
from netshowlib.linux import bridge as linux_bridge
from netshowlib.cumulus import mstpd


class MstpctlStpBridge(object):
    """
    class responsible to managing stp info gathered from mstpctl
    """
    def __init__(self, bridge, cache):
        self.bridge = bridge
        self._root_priority = None
        self._bridge_priority = None
        if cache:
            self.cache = cache
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
    pass

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


