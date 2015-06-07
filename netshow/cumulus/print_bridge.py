# pylint: disable=E0611
# pylint: disable=E1101
"""
Print and Analysis Module for Linux bridge interfaces
"""
from netshow.cumulus import print_iface as cumulus_print_iface
from netshow.linux import print_bridge as linux_print_bridge
from netshowlib.linux import common as linux_common
from datetime import timedelta
from tabulate import tabulate
from netshow.cumulus.common import _


class PrintBridgeMember(cumulus_print_iface.PrintIface,
                        linux_print_bridge.PrintBridgeMember):
    """
    Print and Analysis Class for Linux bridge member interfaces
    """
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
            return _('vlan_aware_bridge')
        return ''

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

    def stp_mode(self):
        stp_mode = self.iface.stp.mode
        if stp_mode == 0:
            _str = _('802.1d / per vlan instance')
        elif stp_mode == 1:
            _str = _('802.1d / single instance')
        elif stp_mode == 2:
            _str = _('RSTP / per vlan instance')
        elif stp_mode == 3:
            _str = _('RSTP / single instance')

        return _str

    def root_port(self):
        ":return: root port in the form of a list"
        if self.iface.stp:
            _stproot = self.iface.stp.root_port
            if _stproot != 'none':
                return [_stproot]
        return [_('root_switch')]

    def designated_ports(self):
        if self.iface.stp:
            portlist = self.iface.stp.member_state.get('designated')
            portnames = [x.name for x in portlist]
            if portlist:
                return linux_common.group_ports(portnames)
        return [_('none')]

    def alternate_ports(self):
        if self.iface.stp:
            portlist = self.iface.stp.member_state.get('alternate')
            portnames = [x.name for x in portlist]
            if portlist:
                return linux_common.group_ports(portnames)
        return [_('none')]

    def last_topo_change_human_time(self):
        """
        :return: last topology change in human readable terms
        """
        last_topo = self.iface.stp.stpdetails.get('time_since_topology_change')
        last_topo_int = int(last_topo.split('s')[0])
        return str(timedelta(seconds=last_topo_int))

    def last_topo_port(self):
        """
        :return: port that received the last topology notification
        """
        return self.iface.stp.stpdetails.get('topology_change_port')

    def last_tcn_field(self):
        """
        :return: last topology change info. Port followed by time
        """
        if self.iface.stp:
            return "%s (%s)" % (self.last_topo_port(),
                                self.last_topo_change_human_time())

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
        _table.append([_('last_tcn') + ':', self.last_tcn_field()])
        if self.iface.vlan_filtering:
            _table.append([_('bridge_type'), _('vlan_aware_bridge')])
        else:
            _table.append(self.vlan_id_field().split())
        return tabulate(_table, _header) + self.new_line()

    def cli_output(self):
        """
        :return: output for 'netshow interface <ifacename> for a
        bridge interface for cumulus provider
        """
        _str = self.cli_header()
        _ip_details = self.ip_details()
        if _ip_details:
            _str += _ip_details
        if self.iface.stp:
            _str += self.stp_details()
            for _state in ['discarding', 'forwarding', 'backup',
                           'oper_edge_port', 'network_port']:
                _str += self.ports_of_some_kind_of_state(_state) + \
                    self.new_line()
        else:
            _str += self.no_stp_details() + self.new_line()

        return _str
