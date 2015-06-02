""" This module is responsible for finding properties
related to bond interface and bond member interfaces """
import netshowlib.cumulus.bridge as cumulus_bridge
import netshowlib.linux.bond as linux_bond
from netshowlib.cumulus import lacp
from netshowlib.cumulus import iface as cumulus_iface
from collections import OrderedDict

class BondMember(cumulus_iface.Iface, linux_bond.BondMember):
    def __init__(self, name, cache=None, master=None):
        cumulus_iface.Iface.__init__(self, name, cache)
        linux_bond.BondMember.__init__(self, name, cache)


class Bond(linux_bond.Bond):
    """ Class for managing Bond on Cumulus Linux """
    def __init__(self, name, cache=None):
        linux_bond.Bond.__init__(self, name, cache)
        self._clag_enable = 0
        self.bondmem_class = BondMember

    @property
    def members(self):
        """
        :return: list of bond members
        """
        fileoutput = self.read_from_sys('bonding/slaves')
        # if bond member list has changed..clear the bond members hash
        if fileoutput:
            if set(fileoutput.split()) != set(self._members.keys()):
                self._members = OrderedDict()
                for i in fileoutput.split():
                    self._members[i] = self.bondmem_class(i, master=self)
        else:
            self._members = {}

        return self._members

    @property
    def stp(self):
        """
        :run MstpctlStpMember if using mstpd
        :run KernelStpMember if using kernel stp
        """
        stp_state = self.read_from_sys('bridge/stp_state')
        if stp_state == '2':
            self._stp = cumulus_bridge.MstpctlStpBridgeMember(self,
                                                              self._cache)
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
        if not self._clag_enable:
            self._clag_enable = self.read_from_sys('bonding/clag_enable')
        return self._clag_enable
