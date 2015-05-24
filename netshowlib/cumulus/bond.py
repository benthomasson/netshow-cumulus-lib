""" This module is responsible for finding properties
related to bond interface and bond member interfaces """
import netshowlib.cumulus.bridge as cumulus_bridge
import netshowlib.linux.bond as linux_bond
from netshowlib.cumulus import lacp
import netshowlib.linux.common as linux_common


class Bond(linux_bond.Bond):
    """ Class for managing Bond on Cumulus Linux """
    def __init__(self, name, cache=None):
        linux_bond.Bond.__init__(self, name, cache)

    @property
    def stp(self):
        """
        :run MstpctlStpMember if using mstpd
        :run KernelStpMember if using kernel stp
        """
        stp_state = linux_common.read_file_oneline(
            '/proc/sys/net/bridge/bridge-stp-user-space')
        if stp_state == '1':
            self._stp = cumulus_bridge.MstpctlStpBridgeMember(self, self._cache)
        else:
            self._stp = super(Bond, self).stp
        return self._stp

    @property
    def lacp(self):
        """
        :return: :class:`linux.lacp<netshowlib.cumulus.lacp.Lacp>` class instance if \
            bond is in LACP mode

        """
        if self.mode == '4':
            if not self._lacp:
                self._lacp = lacp.Lacp(self.name)
            return self._lacp
        return None

    @property
    def clag_enable(self):
        """
        :return: '1' if bond is part of a Clag
        """
        return self.read_from_sys('bonding/clag_enable')
