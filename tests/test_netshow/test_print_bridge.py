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
import re
import io


class TestPrintBridge(object):
    def setup(self):
        iface = cumulus_bridge.Bridge('br1')
        self.piface = print_bridge.PrintBridge(iface)

    @mock.patch('netshowlib.linux.bridge.os.listdir')
    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_cli_output(self, mock_read_from_sys, mock_exec,
                        mock_os_listdir):
        values10 = {('/sbin/mstpctl showall',):
                    io.open('tests/test_netshowlib/mstpctl_showall').read()}
        mock_exec.side_effect = mod_args_generator(values10)
        values = {('bridge/vlan_filtering', 'br1'): None,
                  ('bridge/stp_state', 'br1', True): '2',
                  ('carrier', 'br1', True): '1',
                  ('operstate', 'br1', True): 'up',
                  ('address', 'br1', True): '11:22:33:44:55:66',
                  ('speed', 'br1', True): '10000',
                  ('ifalias', 'br1', True): None,
                  ('operstate', 'br1', True): 'up',
                  ('mtu', 'br1', True): '1500'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        values4 = {
            ('/sys/class/net/br1/brif',): ['swp3.1', 'swp4.1']
        }
        mock_os_listdir.side_effect = mod_args_generator(values4)
        _output = self.piface.cli_output()
        _outputtable = _output.split('\n')
        # checks to make sure stp details is there
        assert_equals(re.split(r'\s{3,}', _outputtable[10]),
                      ['root_priority:', '32768'])

        assert_equals(_outputtable[17], 'ports in Forwarding state')
        assert_equals(_outputtable[19], 'swp3-4')

    @mock.patch('netshowlib.linux.bridge.os.listdir')
    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_stp_details(self, mock_read_from_sys, mock_exec,
                         mock_os_listdir):
        mock_exec.return_value = io.open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/vlan_filtering', 'br1'): None,
                  ('bridge/stp_state', 'br1', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        values4 = {
            ('/sys/class/net/br1/brif',): ['swp3.1', 'swp4.1']
        }
        mock_os_listdir.side_effect = mod_args_generator(values4)
        _output = self.piface.stp_details()
        assert_equals(re.split(r'\s{3,}', _output.split('\n')[2]),
                      ['stp_mode:', 'RSTP / per vlan instance'])

        assert_equals(re.split(r'\s{3,}', _output.split('\n')[3]),
                      ['root_port:', 'root_switch'])
        assert_equals(re.split(r'\s{3,}', _output.split('\n')[4]),
                      ['ports_in_designated_role:  swp3-4'])
        assert_equals(re.split(r'\s{3,}', _output.split('\n')[5]),
                      ['ports_in_alternate_role:', 'none'])
        assert_equals(re.split(r'\s{3,}', _output.split('\n')[6]),
                      ['root_priority:', '32768'])
        assert_equals(re.split(r'\s{3,}', _output.split('\n')[7]),
                      ['bridge_priority:', '32768'])
        assert_equals(re.split(r'\s{3,}', _output.split('\n')[8]),
                      ['last_tcn:', 'swp4.1 (15 days, 20:34:24)'])
        assert_equals(re.split(r'\s{3,}', _output.split('\n')[9]),
                      ['802.1q_tag:', '1'])

    @mock.patch('netshowlib.linux.bridge.os.listdir')
    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_designated_ports(self, mock_read_from_sys, mock_exec,
                              mock_os_listdir):
        mock_exec.return_value = io.open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/vlan_filtering', 'br1', True): None,
                  ('bridge/stp_state', 'br1', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        values4 = {
            ('/sys/class/net/br1/brif',): ['swp3.1', 'swp4.1']
        }
        mock_os_listdir.side_effect = mod_args_generator(values4)
        assert_equals(self.piface.designated_ports(), ['swp3-4'])

    @mock.patch('netshowlib.linux.bridge.os.listdir')
    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_alternate_ports(self, mock_read_from_sys, mock_exec,
                             mock_os_listdir):
        self.piface.iface = cumulus_bridge.Bridge('br0')
        mock_exec.return_value = io.open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/vlan_filtering', 'br0'): None,
                  ('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        values4 = {
            ('/sys/class/net/br0/brif',): ['swp3', 'swp4']
        }
        mock_os_listdir.side_effect = mod_args_generator(values4)
        assert_equals(self.piface.alternate_ports(), ['swp4'])

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_stp_mode(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = io.open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/vlan_filtering', 'br1'): None,
                  ('bridge/stp_state', 'br1', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        # CIST RSTP
        assert_equals(self.piface.stp_mode(), 'RSTP / per vlan instance')

    @mock.patch('netshowlib.linux.common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_stp_root_port(self, read_from_sys, mock_exec):
        br0 = cumulus_bridge.Bridge('br0')
        self.piface.iface = br0
        mock_exec.return_value = io.open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/vlan_filtering', 'br0', True): None,
                  ('bridge/stp_state', 'br0', True): '2'}
        read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.piface.root_port(), ['swp3'])

    @mock.patch('netshowlib.linux.bridge.os.listdir')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    @mock.patch('netshowlib.linux.common.exec_command')
    @mock.patch('netshowlib.linux.common.read_symlink')
    @mock.patch('netshowlib.linux.iface.Iface.is_l3')
    def test_summary(self, mock_is_l3, mock_read_symlink,
                     mock_exec,
                     mock_read_from_sys,
                     mock_os_listdir):
        mock_is_l3.return_value = True
        values4 = {
            ('/sys/class/net/br1/brif',): ['swp3.1', 'swp4.1']
        }
        mock_os_listdir.side_effect = mod_args_generator(values4)
        values1 = {}
        values2 = {('bridge/stp_state', 'br1', True): '2',
                   ('bridge/vlan_filtering', 'br1'): None}
        mock_read_symlink.side_effect = mod_args_generator(values1)
        mock_read_from_sys.side_effect = mod_args_generator(values2)
        values3 = {('/sbin/mstpctl showall',): io.open(
            'tests/test_netshowlib/mstpctl_showall').read(),
            ('/usr/sbin/lldpctl -f xml',): None}
        mock_exec.side_effect = mod_args_generator(values3)
        self.piface.iface.ip_address.ipv4 = ['10.1.1.1/24']
        assert_equals(self.piface.summary, ['ip: 10.1.1.1/24',
                                            'tagged_members: swp3-4.1', '802.1q_tag: 1',
                                            'stp: rootswitch(32768)'])

    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_is_vlan_aware_bridge(self, mock_read_from_sys):
        values = {('bridge/vlan_filtering', 'br1'): '1'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.piface.is_vlan_aware_bridge(), 'vlan_aware_bridge')

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

        values2 = {('/sbin/mstpctl showall',): io.open(
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

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_speed(self, mock_read_sys):
        values = {('speed', ): '1000',
                  ('carrier',): '1',
                  ('operstate',): 'up'}
        self.piface.iface._asic = {'asicname': 'xe2', 'initial_speed': '10000'}
        mock_read_sys.side_effect = mod_args_generator(values)
        assert_equals(self.piface.speed, '1G(sfp)')

    @mock.patch('netshowlib.linux.common.exec_command')
    @mock.patch('netshowlib.linux.common.read_symlink')
    @mock.patch('netshowlib.linux.iface.Iface.is_bridgemem')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def todo_bridgemem_details_vlan_aware_driver(self,
                                                 mock_read_from_sys,
                                                 mock_is_bridgemem,
                                                 mock_symlink,
                                                 mock_exec):
        values = {('/sbin/mstpctl showall',): open(
            'tests/test_netshowlib/mstpctl_showall').read()}
        mock_exec.side_effect = mod_args_generator(values)
        values2 = {('/sys/class/net/swp22/brport/bridge',): 'br22'}
        mock_symlink.side_effect = mod_args_generator(values2)
        values3 = {('brport/vlans', 'swp22',): open(
            'tests/test_netshowlib/all_vlans.txt').readlines()}
        mock_read_from_sys.side_effect = mod_args_generator(values3)
        _output = self.piface.bridgemem_details()
        _outputtable = _output.split('\n')
        assert_equals(_outputtable[0], 'vlans in disabled state')
        assert_equals(_outputtable[2], '1-10, 20-24, 29-30, 32, 64, 4092')

    @mock.patch('netshowlib.linux.common.read_file_oneline')
    @mock.patch('netshowlib.linux.common.read_file')
    @mock.patch('netshowlib.linux.bridge.os.listdir')
    @mock.patch('netshowlib.linux.common.exec_command')
    @mock.patch('netshowlib.linux.common.read_symlink')
    @mock.patch('netshowlib.linux.iface.Iface.is_bridgemem')
    @mock.patch('netshowlib.cumulus.iface.Iface.stp_state')
    def test_bridgemem_details_classic_driver(self,
                                              mock_stp_state,
                                              mock_is_bridgemem,
                                              mock_symlink,
                                              mock_exec,
                                              mock_listdir,
                                              mock_file,
                                              mock_read_oneline):
        values4 = {('/sys/class/net',): ['swp3', 'swp3.1', 'swp3.2'],
                   ('/sys/class/net/br0/brif',): ['swp3'],
                   ('/sys/class/net/br1/brif',): ['swp3.1'],
                   ('/sys/class/net/br2/brif',): ['swp3.2']
                   }
        mock_is_bridgemem.return_value = True
        mock_stp_state.return_value = '2'
        mock_listdir.side_effect = mod_args_generator(values4)
        mock_exec.return_value = io.open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state',): '2',
                  ('brport/vlans',): None,
                  ('/sys/class/net/swp3/brport/vlans',): None}
        mock_read_oneline.side_effect = mod_args_generator(values)
        values5 = {
            ('/sys/class/net/swp3/brport/bridge',): 'br0',
            ('/sys/class/net/swp3.1/brport/bridge',): 'br1',
            ('/sys/class/net/swp3.2/brport/bridge',): 'br2'
        }
        mock_symlink.side_effect = mod_args_generator(values5)
        self.piface.iface = cumulus_bridge.BridgeMember('swp3')
        _output = self.piface.bridgemem_details()
        _outputtable = _output.split('\n')
#        assert_equals(_outputtable[0], 'vlans in Root state')
#        assert_equals(_outputtable[2], 'br0')
#        assert_equals(_outputtable[4], 'vlans in Designated state')
#        assert_equals(_outputtable[6], 'br1(1)')
#        assert_equals(_outputtable[8], 'vlans in Forwarding state')
#        assert_equals(_outputtable[10], 'br0, br1(1)')
#        assert_equals(_outputtable[12], 'vlans in Discarding state')
#        assert_equals(_outputtable[14], 'br2(2)')
#        assert_equals(_outputtable[16], 'vlans in Oper Edge Port state')
#        assert_equals(_outputtable[18], 'br1(1)')
#        assert_equals(_outputtable[20], 'vlans in Network Port state')
#        assert_equals(_outputtable[22], 'br0')
#        assert_equals(_outputtable[24], 'vlans in Backup state')
#        assert_equals(_outputtable[26], 'br2(2)')

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
