# pylint: disable=E0611
# pylint: disable=E1101
"""
Print and Analysis Module for Linux bridge interfaces
"""
from netshow.cumulus.print_iface import PrintIface
from netshow.linux import print_bridge as linux_print_bridge
from netshowlib.linux import common as linux_common

from flufl.i18n import initialize
from tabulate import tabulate

_ = initialize('netshow-cumulus-lib')


class PrintBridgeMember(PrintIface):
    """
    Print and Analysis Class for Linux bridge member interfaces
    """
    @property
    def port_category(self):
        """
        :return: port category for bridge member
        """
        return linux_print_bridge.PrintBridgeMember.port_category.fget(self)

    @property
    def summary(self):
        """
        :return: summary info regarding a bridge member
        """
        return linux_print_bridge.PrintBridgeMember.summary.fget(self)

    @classmethod
    def _pretty_vlanlist(cls, bridgelist):
        """
        :return: list of vlans that match category. First list of \
            native ports, then vlan ids of tagged bridges MODIFY
        """
        return linux_print_bridge.PrintBridgeMember._pretty_vlanlist(
            bridgelist)

    def bridgemem_details(self):
        """
        :return: list vlans or bridge names of various stp states MODIFY
        """
        # check if port is in STP
        _str = ''
        if self.iface.vlan_filtering:
            _vlanlist = self.iface.vlan_list
        _stpstate = self.iface.stp.state
        # get the list of states by grabbing all the keys
        for _state, _bridgelist in _stpstate.items():
            if _bridgelist:
                _header = [_("vlans in %s state" % (_state))]
                # if vlan aware and bridgelist is not empty, then assume
                # all vlans have that stp state
                if self.iface.vlan_filtering:
                    _table = [[', '.join(linux_common.create_range(
                        '', _vlanlist))]]
                else:
                    _table = [self._pretty_vlanlist(_bridgelist)]

                _str += tabulate(_table, _header, numalign='left') + self.new_line()

        return _str

    def cli_output(self):
        """
        :return: output for 'netshow interface <ifacename> for a bridge interface' MODIFY
        """
        _str = self.cli_header() + self.new_line()
        _str += self.bridgemem_details() + self.new_line()
        _str += self.counters_summary() + self.new_line()
        _str += self.lldp_details() + self.new_line()

        return _str


class PrintBridge(linux_print_bridge.PrintBridge):
    """
    Print and Analysis Class for Cumulus bridge interfaces
    Inherits from PrintBridge from Linux provider because it
    doesn't need any of the PrintIface functions from the cumulus Provider.
    But does need to inherit most of the PrintBridge functions from the
    Linux Provider.
    """

    def is_vlan_aware_bridge(self):
        if self.iface.vlan_filtering:
            return _('vlan aware bridge')
        return ''

    def root_port(self):
        ":return: root port in the form of a list"
        pass

    @property
    def summary(self):
        """
        :return: summary information regarding the bridge
        """
        _info = []
        _info.append(self.untagged_ifaces())
        if not self.iface.vlan_filtering:
            _info.append(self.tagged_ifaces())
        _info.append(self.vlan_id_field())
        _info.append(self.stp_summary())
        _info.append(self.is_vlan_aware_bridge())
        return [x for x in _info if x]

    def stp_details(self):
        """
        :return: stp details for the bridge interface
        """
        _header = [_(''), '']
        _table = []
        _table.append([_('stp_mode') + ':', self.stp_mode()])
        _table.append([_('root_port') + ':', ', '.join(self.root_port())])
        _table.append([_('ports_in_designated_role') + ':',
                       ', '.join(self.designated_ports())])
        _table.append([_('ports_in_alternate_role') + ':',
                       ', '.join(self.alternate_ports())])
        _table.append([_('root_priority') + ':', self.iface.stp.root_priority])
        _table.append([_('bridge_priority') + ':',
                       self.iface.stp.bridge_priority])
        _table.append([_('last_tcn') + ':', self.iface.stp.last_tcn()])
        _table.append(self.vlan_id_field().split())
        return tabulate(_table, _header)

    def cli_output(self):
        pass
