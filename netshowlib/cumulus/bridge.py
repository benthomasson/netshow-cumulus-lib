"""
Bridge module for the cumulus provider
"""

from netshowlib.cumulus import iface as cumulus_iface


class Bridge(cumulus_iface.Iface):
    """ Bridge class for the cumulus provider
    """
    def __init__(self, name, cache=None):
        cumulus_iface.Iface.__init__(self, name, cache)
        self._vlan_filtering = 0

    @property
    def vlan_filtering(self):
        """
        :return the vlan filtering setting. If set to 1 trunk config is placed
         under the physical port and can be seen using bridge vlan show command
        """
        self._vlan_filtering = 0
        if self.is_vlan_aware_bridge():
            self._vlan_filtering = 1
        return self._vlan_filtering
