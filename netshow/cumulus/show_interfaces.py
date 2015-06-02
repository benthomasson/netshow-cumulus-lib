# pylint: disable=R0902
# pylint: disable=W0232
# pylint: disable=C0325
# pylint: disable=W0232
# pylint: disable=E0611
# pylint: disable=E1101
"""
Module for printout of 'netshow interfaces' of the Cumulus provider
"""

import netshow.linux.print_iface as linux_printiface
import netshow.cumulus.print_iface as print_iface
import netshow.cumulus.print_bridge as print_bridge
import netshow.cumulus.print_bond as print_bond
import netshowlib.cumulus.cache as cumulus_cache
from netshowlib.linux import iface as linux_iface
import json
from netshow.linux.netjson_encoder import NetEncoder
from flufl.i18n import initialize

_ = initialize('netshow-cumulus-lib')


class ShowInterfaces(linux_printiface.PrintIface):
    """ Class responsible for the 'netshow interfaces' printout for \
        the cumulus provider
    """

    def __init__(self, **kwargs):
        self._ifacelist = {}
        self.show_mac = kwargs.get('--mac') or kwargs.get('-m')
        self.use_json = kwargs.get('--json') or kwargs.get('-j')
        self.show_all = True
        self.show_mgmt = kwargs.get('mgmt')
        self.show_bridges = kwargs.get('bridges')
        self.show_bond = kwargs.get('bond')
        self.show_bondmem = kwargs.get('bondmem')
        self.show_access = kwargs.get('access')
        self.show_trunk = kwargs.get('trunk')
        self.show_l3 = kwargs.get('l3')
        self.show_l2 = kwargs.get('l2')
        self.show_phy = kwargs.get('phy')
        self.single_iface = kwargs.get('<iface>')
        if kwargs.get('all') or self.single_iface is not None:
            self.show_up = False
        else:
            self.show_up = True
            if self.show_bond or self.show_bondmem \
                    or self.show_access or self.show_trunk \
                    or self.show_bridges or self.show_mgmt:
                self.show_all = False

        self.oneline = kwargs.get('--oneline') or kwargs.get('-1')
        self.iface_categories = ['bond', 'bondmem', 'bridges',
                                 'trunk', 'access', 'l3', 'l2']
        self._initialize_ifacelist()

    def print_single_iface(self):
        """
        :return: netshow terminal output or JSON of a single iface
        """
        feature_cache = cumulus_cache.Cache()
        feature_cache.run()
        _printiface = print_iface.iface(self.single_iface, feature_cache)
        if not _printiface:
            return _('interface_does_not_exist')

        if self.use_json:
            return json.dumps(_printiface,
                              cls=NetEncoder, indent=4)
        else:
            return _printiface.cli_output()

    @property
    def ifacelist(self):
        """
        :return: hash of interface categories. each category containing a list of \
            iface pointers to interfaces that belong in that category. For example
           ifacelist['bridges'] points to a list of bridge Ifaces.
        """

        # ifacelist is already populated..
        # to reset set ``self._ifacelist = None``
        if len(self._ifacelist.get('all')) > 0:
            return self._ifacelist

        self._initialize_ifacelist()
        list_of_ports = linux_iface.portname_list()
        feature_cache = cumulus_cache.Cache()
        feature_cache.run()
        for _portname in list_of_ports:
            _printiface = print_iface.iface(_portname, feature_cache)

            # if iface is a l2 subint bridgemem, then ignore
            if _printiface.iface.is_subint() and \
                    isinstance(_printiface, print_bridge.PrintBridgeMember):
                continue

            self._ifacelist['all'][_portname] = _printiface

            # mutual exclusive bond/bridge/bondmem/bridgemem
            if isinstance(_printiface, print_bridge.PrintBridge):
                self._ifacelist['bridges'][_portname] = _printiface
                self._ifacelist['l2'][_portname] = _printiface
            elif isinstance(_printiface, print_bond.PrintBond):
                self._ifacelist['bond'][_portname] = _printiface
            elif isinstance(_printiface, print_bridge.PrintBridgeMember):
                self._ifacelist['l2'][_portname] = _printiface
            elif isinstance(_printiface, print_bond.PrintBondMember):
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
