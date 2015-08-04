# pylint: disable=R0902
# pylint: disable=W0232
# pylint: disable=C0325
# pylint: disable=W0232
# pylint: disable=E0611
# pylint: disable=E1101
"""
Module for printout of 'netshow interfaces' of the Cumulus provider
"""
from netshowlib import netshowlib as nn
import netshow.linux.show_interfaces as linux_showint
import netshow.cumulus.print_iface as print_iface
import netshow.cumulus.print_bridge as print_bridge
import netshow.cumulus.print_bond as print_bond
import netshowlib.cumulus.cache as cumulus_cache
from netshowlib.cumulus import iface
from netshow.linux.netjson_encoder import NetEncoder
import json
from netshow.linux.common import legend
from netshow.cumulus.common import _


class ShowInterfaces(linux_showint.ShowInterfaces):
    """ Class responsible for the 'netshow interfaces' printout for \
        the cumulus provider
    """

    def __init__(self, _cl):
        linux_showint.ShowInterfaces.__init__(self, _cl)
        self.iface_categories = self.iface_categories + ['phy', 'mgmt']
        self.show_phy = _cl.get('phy')
        self.cache = cumulus_cache
        self.print_iface = print_iface
        self.print_bridge = print_bridge
        self.print_bond = print_bond
        self.iface = iface

    def print_single_iface(self):
        """
        :return: netshow terminal output or JSON of a single iface
        """
        feature_cache = self.cache.Cache()
        feature_cache.run()
        _printiface = self.print_iface.iface(self.single_iface, feature_cache)
        if not _printiface:
            return _('interface_does_not_exist')

        if self.use_json:
            return json.dumps(_printiface,
                              cls=NetEncoder, indent=4)
        else:
            return _printiface.cli_output() + legend(self.show_legend)

    @property
    def ifacelist(self):
        """
        :return: hash of interface categories. each category containing a list of \
            iface pointers to interfaces that belong in that category. For example
           ifacelist['bridges'] points to a list of bridge Ifaces.
           TODO: refactor!
        """

        # ifacelist is already populated..
        # to reset set ``self._ifacelist = None``
        if len(self._ifacelist.get('all')) > 0:
            return self._ifacelist

        self._initialize_ifacelist()
        list_of_ports = sorted(nn.portname_list())
        feature_cache = self.cache.Cache()
        feature_cache.run()
        for _portname in list_of_ports:
            _printiface = self.print_iface.iface(_portname, feature_cache)
            if self.show_up and _printiface.iface.linkstate < 2:
                continue
            # if iface is a l2 subint bridgemem, then ignore
            if _printiface.iface.is_subint() and \
                    isinstance(_printiface, self.print_bridge.PrintBridgeMember):
                continue

            self._ifacelist['all'][_portname] = _printiface

            if isinstance(_printiface.iface, self.iface.Iface):
                if _printiface.iface.is_phy():
                    self._ifacelist['phy'][_portname] = _printiface
                elif _printiface.iface.is_mgmt():
                    self._ifacelist['mgmt'][_portname] = _printiface

            # mutual exclusive bond/bridge/bondmem/bridgemem
            if isinstance(_printiface, self.print_bridge.PrintBridge):
                self._ifacelist['bridge'][_portname] = _printiface
                self._ifacelist['l2'][_portname] = _printiface
            elif isinstance(_printiface, self.print_bond.PrintBond):
                self._ifacelist['bond'][_portname] = _printiface
                if _printiface.iface.is_bridgemem():
                    self._ifacelist['l2'][_portname] = _printiface
            elif isinstance(_printiface, self.print_bridge.PrintBridgeMember):
                self._ifacelist['l2'][_portname] = _printiface
            elif isinstance(_printiface, self.print_bond.PrintBondMember):
                self._ifacelist['bondmem'][_portname] = _printiface
                continue

            # mutual exclusive - l3/trunk/access
            if _printiface.iface.is_l3():
                self._ifacelist['l3'][_portname] = _printiface
            elif _printiface.iface.is_trunk():
                self._ifacelist['trunk'][_portname] = _printiface
            elif _printiface.iface.is_access():
                self._ifacelist['access'][_portname] = _printiface

        return self._ifacelist
