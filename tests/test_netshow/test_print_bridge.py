# http://pylint-messages.wikidot.com/all-codes
# attribute defined outside init
# pylint: disable=W0201
# pylint: disable=R0913
# disable unused argument
# pylint: disable=W0613
# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# disable invalid name
# pylint: disable=C0103
# pylint: disable=F0401
# pylint: disable=E0611
# pylint: disable=W0611

import netshow.cumulus.print_bridge as print_bridge
import netshowlib.cumulus.bridge as cumulus_bridge
import mock
from asserts import assert_equals, mod_args_generator
from nose.tools import set_trace


class TestPrintBridge(object):
    def setup(self):
        iface = cumulus_bridge.Bridge('br1')
        self.piface = print_bridge.PrintBridge(iface)

    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_summary(self, mock_read_from_sys):
        values = {('bridge/vlan_filtering', 'br1'): '1'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.piface.is_vlan_aware_bridge(), 'vlan aware bridge')

        values = {('bridge/vlan_filtering', 'br1'): None}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.piface.is_vlan_aware_bridge(), '')


    @mock.patch('netshowlib.linux.common.exec_command')
    @mock.patch('netshowlib.linux.common.read_symlink')
    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_stp_summary(self,
                         mock_read_sys,
                         mock_symlink,
                         mock_exec):

        values2 = {('/sbin/mstpctl showall',): open(
            'tests/test_netshowlib/mstpctl_showall').read()}
        mock_exec.side_effect = mod_args_generator(values2)

        # vlans are 1-10,20-24,29-30,32,64,4092
        values = {('bridge/stp_state',): '2'}
        mock_read_sys.side_effect = mod_args_generator(values)

        _output = self.piface.stp_summary()
        assert_equals(_output, 'stp: rootswitch(32768)')
class TestPrintBridgeMember(object):
    def setup(self):
        iface = cumulus_bridge.BridgeMember('swp22')
        self.piface = print_bridge.PrintBridgeMember(iface)

    @mock.patch('netshowlib.linux.common.exec_command')
    @mock.patch('netshowlib.linux.common.read_symlink')
    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_bridgemem_details_vlan_aware_driver(self,
                                                 mock_read_sys,
                                                 mock_symlink,
                                                 mock_exec):

        values2 = {('/sbin/mstpctl showall',): open(
            'tests/test_netshowlib/mstpctl_showall').read()}
        mock_exec.side_effect = mod_args_generator(values2)
        values3 = {('/sys/class/net/swp22/brport/bridge',): 'br22'}
        mock_symlink.side_effect = mod_args_generator(values3)

        # vlans are 1-10,20-24,29-30,32,64,4092
        values = {('bridge/stp_state',): '2',
                  ('brport/vlans',): open(
                      'tests/test_netshowlib/all_vlans.txt').readlines()}
        mock_read_sys.side_effect = mod_args_generator(values)
        _output = self.piface.bridgemem_details()
        _outputtable = _output.split('\n')
        assert_equals(_outputtable[0], 'vlans in disabled state')
        assert_equals(_outputtable[2], '1-10, 20-24, 29-30, 32, 64, 4092')

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    @mock.patch('netshowlib.linux.bridge.os.listdir')
    @mock.patch('netshowlib.linux.common.exec_command')
    @mock.patch('netshowlib.linux.common.read_symlink')
    def test_bridgemem_details_classic_driver(self,
                                              mock_symlink,
                                              mock_exec,
                                              mock_listdir,
                                              mock_read_sys):
        values4 = {('/sys/class/net',): ['swp3', 'swp3.1', 'swp3.2'],
                   ('/sys/class/net/br0/brif',): ['swp3'],
                   ('/sys/class/net/br1/brif',): ['swp3.1'],
                   ('/sys/class/net/br2/brif',): ['swp3.2']
                   }
        mock_listdir.side_effect = mod_args_generator(values4)
        mock_exec.return_value = open(
            'tests/test_netshowlib/mstpctl_showall').read()
        # vlans are 1-10,20-24,29-30,32,64,4092
        values = {('bridge/stp_state',): '2',
                  ('brport/vlans',): None}
        mock_read_sys.side_effect = mod_args_generator(values)
        values5 = {
            ('/sys/class/net/swp3/brport/bridge',): 'br0',
            ('/sys/class/net/swp3.1/brport/bridge',): 'br1',
            ('/sys/class/net/swp3.2/brport/bridge',): 'br2'
        }
        mock_symlink.side_effect = mod_args_generator(values5)
        self.piface.iface._name = 'swp3'
        _output = self.piface.bridgemem_details()
        _outputtable = _output.split('\n')
        assert_equals(_outputtable[0], 'vlans in root state')
        assert_equals(_outputtable[2], 'br0')
        assert_equals(_outputtable[4], 'vlans in designated state')
        assert_equals(_outputtable[6], '1')
        assert_equals(_outputtable[8], 'vlans in forwarding state')
        assert_equals(_outputtable[10], 'br0, 1')
        assert_equals(_outputtable[12], 'vlans in discarding state')
        assert_equals(_outputtable[14], '2')
        assert_equals(_outputtable[16], 'vlans in edge_port state')
        assert_equals(_outputtable[18], '1')
        assert_equals(_outputtable[20], 'vlans in network_port state')
        assert_equals(_outputtable[22], 'br0')
        assert_equals(_outputtable[24], 'vlans in backup state')
        assert_equals(_outputtable[26], '2')

    def test_port_category(self):
        # call the linux bridge member port_category function
        assert_equals(self.piface.port_category, 'access/l2')

    @mock.patch('netshow.linux.print_iface.linux_iface.Iface.is_trunk')
    @mock.patch('netshow.linux.print_iface.PrintIface.access_summary')
    def test_summary(self, mock_access_summary, mock_is_trunk):
        mock_is_trunk.return_value = False
        mock_access_summary.return_value = 'access summary'
        # call the linux bridge member summary function
        assert_equals(self.piface.summary, 'access summary')
