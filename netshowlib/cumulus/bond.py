""" This module is responsible for finding properties
related to bond interface and bond member interfaces """
import netshowlib.cumulus.bridge as cumulus_bridge
import netshowlib.linux.bond as linux_bond
from netshowlib.cumulus import lacp
from netshowlib.cumulus import iface as cumulus_iface


class BondMember(cumulus_iface.Iface):
    def __init__(self, name, cache=None, master=None):
        cumulus_iface.Iface.__init__(self, name, cache)
        self._master = master
        self._linkfailures = 0
        self._bondstate = None

    def _parse_proc_net_bonding(self):
        return linux_bond.BondMember._parse_proc_net_bonding(self)

    @property
    def master(self):
        """
        :return: pointer to  :class:`Bond<netshowlib.linux.bond.Bond>` \
        instance that \
        this interface belongs to
        """
        return linux_bond.BondMember.master.fget(self)

    @property
    def bondstate(self):
        """
        :return: state of interface in the bond. can be \
            0(inactive) or 1(active)
        """
        return linux_bond.BondMember.bondstate.fget(self)

    @property
    def linkfailures(self):
        """
        number of mii transitions bond member reports while the bond is \
            active
        this counter cannot be cleared. will reset when the bond is \
            reinitialized
        via the ifdown/ifup process

        :return: number of mii transitions
        """
        return linux_bond.BondMember.linkfailures.fget(self)


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
        return self.read_from_sys('bonding/clag_enable')
