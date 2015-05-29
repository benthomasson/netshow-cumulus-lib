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


class PrintBridge(PrintIface):
    """
    Print and Analysis Class for Cumulus bridge interfaces
    """

    def __init__(self, iface):
        PrintIface.__init__(self, iface)
        self.linux_piface = linux_print_bridge.PrintBridge(iface)

    def untagged_ifaces(self):
        return self.linux_piface.untagged_ifaces()

    def tagged_ifaces(self):
        return self.linux_piface.tagged_ifaces()

    def vlan_id_field(self):
        return self.linux_piface.vlan_id_field()

    def stp_summary(self):
        """
        Leverages function call from linux provider. Wraps cumulus Iface in linux provider
        and calls
        :return: stp summary info.
        """
        return self.linux_piface.stp_summary()

    def is_vlan_aware_bridge(self):
        if self.iface.vlan_filtering:
            return _('vlan aware bridge')
        return ''

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
