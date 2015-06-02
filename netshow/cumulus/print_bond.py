# pylint: disable=e0611
# pylint: disable=e1101
"""
Print and Analysis Module for Linux bond interfaces
"""

from netshow.cumulus import print_iface as cumulus_print_iface
import netshow.linux.print_bond as linux_print_bond

from flufl.i18n import initialize
from tabulate import tabulate
_ = initialize('netshow-cumulus-lib')


class PrintBondMember(linux_print_bond.PrintIface):
    """
    Print and Analysis Class for Linux bond member interfaces
    """

    @property
    def connector_type(self):
        """
        :return call of connector type from CUmulus PrintIface function
        """
        return cumulus_print_iface.PrintIface.connector_type.fget(self)

    @property
    def speed(self):
        """
        :return: call speed from Cumulus PrintIface function
        """
        return cumulus_print_iface.PrintIface.speed.fget(self)

    def bondmem_details(self):
        """
        :return: string with output shown when netshow interfaces is issued on a \
        bond member
        """
        _header = [_('bond_details'), '']
        _master = self.iface.master
        _printbond = PrintBond(_master)
        _table = []
        _table.append([_('master_bond') + ':', _master.name])
        _table.append([_('state_in_bond') + ':', self.state_in_bond])
        _table.append([_('link_failures') + ':', self.iface.linkfailures])
        _table.append([_('bond_members') + ':', ', '.join(_master.members.keys())])
        _table.append([_('bond_mode') + ':', _printbond.mode])
        _table.append([_('load_balancing') + ':', _printbond.hash_policy])
        _table.append([_('minimum_links') + ':', _master.min_links])
        _lacp_info = self.iface.master.lacp
        if _lacp_info:
            _table.append([_('lacp_sys_priority') + ':', _master.lacp.sys_priority])
            _table.append([_('lacp_rate') + ':', _printbond.lacp_rate()])

        return tabulate(_table, _header)

    def cli_output(self):
        """
        cli output of the linux bond member interface
        :return: output for 'netshow interface <ifacename>'
        """
        _str = self.cli_header() + self.new_line()
        _str += self.bondmem_details() + self.new_line()
        _str += cumulus_print_iface.PrintIface.counters_summary(self) + self.new_line()
        _str += self.lldp_details() + self.new_line()
        return _str


class PrintBond(linux_print_bond.PrintBond):
    """
    Print and Analysis Class for Linux bond interfaces
    """
    @property
    def port_category(self):
        """
        :return: port category for a bond
        """
        if self.iface.is_l3():
            return _('bond/l3')
        elif self.iface.is_trunk():
            return _('bond/trunk')
        elif self.iface.is_access():
            return _('bond/access')
        else:
            return _('bond')

    @property
    def summary(self):
        """
        :return: summary info for bonds for 'netshow interfaces'
        """
        _arr = []
        _arr.append(self.print_bondmems())
        if self.iface.is_l3():
            _arr.append(', '.join(self.iface.ip_address.allentries))
        elif self.iface.is_trunk():
            _arr += self.trunk_summary()
        elif self.iface.is_access():
            _arr += self.access_summary()
        return _arr

    @property
    def hash_policy(self):
        """
        :return: hash policy for bond
        """
        _hash_policy = self.iface.hash_policy
        if _hash_policy == '1':
            return _('layer3+4')
        elif _hash_policy == '2':
            return _('layer2+3')
        elif _hash_policy == '0':
            return _('layer2')
        else:
            return _('unknown')

    @property
    def mode(self):
        """
        :return: name of the bond mode
        """
        _mode = self.iface.mode
        if _mode == '4':
            return _('lacp')
        elif _mode == '3':
            return _('broadcast')
        elif _mode == '2':
            return _('balance-xor')
        elif _mode == '1':
            return _('active-backup')
        elif _mode == '0':
            return _('balance-rr')
        else:
            return _('unknown')

    @classmethod
    def abbrev_bondstate(cls, bondmem):
        """
        :param bondmem: :class:`netshowlib.linux.BondMember` instance
        :return: 'P' if bondmem in bond
        :return: 'D' if bondmem is not in bond
        """
        if bondmem.bondstate == 1:
            return _('P')
        else:
            return _('D')

    def print_bondmems(self):
        """
        :return: bondmember list when showing summary in netshow interfaces \
            for the bond interface
        """
        _arr = []
        for _bondmem in self.iface.members.values():
            _arr.append("%s(%s%s)" % (_bondmem.name,
                                      self.abbrev_linksummary(_bondmem),
                                      self.abbrev_bondstate(_bondmem)))
        if len(_arr) > 0:
            return ': '.join([_('bondmems'), ', '.join(sorted(_arr))])
        else:
            return _('no_bond_members_found')

    def lacp_rate(self):
        """
        :return: lacp rate in plain english
        """
        _lacp = self.iface.lacp
        if _lacp:
            if _lacp.rate == '1':
                return _('fast_lacp')
            elif _lacp.rate == '0':
                return _('slow_lacp')
            else:
                return _('unknown')

    def bond_details(self):
        """
        print out table with bond details for netshow interface [ifacename]
        """
        _header = [_('bond_details'), '']
        _table = []
        _table.append([_('bond_mode') + ':', self.mode])
        _table.append([_('load_balancing') + ':', self.hash_policy])
        _table.append([_('minimum_links') + ':', self.iface.min_links])
        _lacp_info = self.iface.lacp
        if _lacp_info:
            _table.append([_('lacp_sys_priority') + ':', self.iface.lacp.sys_priority])
            _table.append([_('lacp_rate') + ':', self.lacp_rate()])
        return tabulate(_table, _header)

    def bondmem_details(self):
        """
        print out table with bond member summary info for netshow interface [ifacename]
        for bond interface
        """
        _header = ['', _('port'), _('speed'), _('link_failures')]
        _table = []
        _bondmembers = self.iface.members.values()
        if len(_bondmembers) == 0:
            return _('no_bond_members_found')

        for _bondmem in _bondmembers:
            _printbondmem = PrintBondMember(_bondmem)
            _table.append([_printbondmem.linkstate,
                           "%s(%s)" % (_printbondmem.name,
                                       self.abbrev_bondstate(_bondmem)),
                           _printbondmem.speed,
                           _bondmem.linkfailures])

        return tabulate(_table, _header)

    def lldp_details(self):
        """
        :return: lldp info for the bond members
        """
        _header = [_('lldp'), '', '']
        _table = []
        for _bondmem in self.iface.members.values():
            lldp_output = _bondmem.lldp
            if not lldp_output:
                continue
            _table.append(["%s(%s)" % (_bondmem.name,
                                       self.abbrev_bondstate(_bondmem)),
                           '====',
                           "%s(%s)" % (lldp_output[0].get('adj_port'),
                                       lldp_output[0].get('adj_hostname'))])
            del lldp_output[0]
            for _entry in lldp_output:
                _table.append(['', '====',
                               "%s(%s)" % (_entry.get('adj_port'),
                                           _entry.get('adj_hostname'))])

        if len(_table) > 0:
            return tabulate(_table, _header)
        else:
            return _('no_lldp_entries')

    def cli_output(self):
        """
        cli output of the linux bond interface
        :return: output for 'netshow interface <ifacename>'
        """
        _str = self.cli_header() + self.new_line()
        _str += self.bond_details() + self.new_line()
        _str += self.ip_details() + self.new_line()
        _str += self.bondmem_details() + self.new_line()
        _str += self.lldp_details() + self.new_line()
        return _str
