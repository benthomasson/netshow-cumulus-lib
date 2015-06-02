# pylint: disable=W0232
# pylint: disable=E0611
# pylint: disable=E1101
"""
Cumulus Iface module with print functions
"""
from netshowlib import netshowlib as nn
from netshowlib.cumulus import iface as cumulus_iface
from netshow.linux import print_iface as linux_printiface
from flufl.i18n import initialize
from tabulate import tabulate
import re

_ = initialize('netshow-cumulus-lib')


def iface(name, cache=None):
    """
    :return: ``:class:PrintIface`` instance that matches \
        correct iface type of the named interface
    :return: None if interface does not exist
    """
    # create test iface.
    from nose.tools import set_trace; set_trace()
    test_iface = cumulus_iface.iface(name, cache=cache)
    if not test_iface.exists():
        return None
    if test_iface.is_bridge():
        bridge = nn.import_module('netshow.cumulus.print_bridge')
        return bridge.PrintBridge(test_iface)
    elif test_iface.is_bridgemem():
        bridge = nn.import_module('netshow.cumulus.print_bridge')
        return bridge.PrintBridgeMember(test_iface)
    elif test_iface.is_bond():
        bond = nn.import_module('netshow.cumulus.print_bond')
        return bond.PrintBond(test_iface)
    elif test_iface.is_bondmem():
        bondmem = nn.import_module('netshow.cumulus.print_bond')
        return bondmem.PrintBondMember(test_iface)
    return PrintIface(test_iface)


class PrintIface(linux_printiface.PrintIface):
    """
    Cumulus Iface class with print functions
    """
    @property
    def connector_type(self):
        """
        :return: prints out string for connector type
        """
        _connector = self.iface.connector_type
        if _connector == 4:
            return _('4x10g')
        elif _connector == 3:
            return _('qsfp')
        elif _connector == 2:
            return _('sfp')
        elif _connector == 1:
            return _('rj45')

    @property
    def port_category(self):
        """
        :return: port type. Via interface discovery determine classify port \
        type
        """
        if self.iface.is_mgmt():
            return _('mgmt')
        elif self.iface.is_svi():
            return _('svi/l3')
        else:
            return super(PrintIface, self).port_category

    @property
    def speed(self):
        """
        used by the functions that print speed info on cumulus linux.
        :return: speed + connector type in one print statement.
        """
        _connector_type = self.connector_type
        _speed = linux_printiface.PrintIface.speed.fget(self)
        if _connector_type:
            return "%s(%s)" % (_speed, _connector_type)
        else:
            return _speed

    def cli_output(self):
        """
        Each PrintIface child should define their own  of this function
        :return: output for 'netshow interface <ifacename>'
        """
        _str = self.cli_header() + self.new_line()
        _str += self.ip_details() + self.new_line()
        _str += self.counters_summary() + self.new_line()
        _str += self.lldp_details() + self.new_line()
        return _str


    def counters_summary(self):
        """
        if counters are available print a summary of the counters.
        """
        _counters = self.iface.counters
        if not _counters:
            return ''
        _counters_all = _counters.all
        _header = [_('counters'), _('tx'), _('rx')]
        _table = []
        for _countername in ['errors', 'unicast', 'broadcast', 'multicast']:
            _table.append([_(_countername),
                           _counters_all.get('tx').get(_countername),
                           _counters_all.get('rx').get(_countername)])
        # keep return in the right place please!
        return tabulate(_table, _header)
