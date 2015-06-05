# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.cumulus.bridge as cumulus_bridge
from netshowlib.linux import bridge as linux_bridge
import mock
from asserts import assert_equals, mod_args_generator


class TestCumulusBridgeMember(object):

    def setup(self):
        self.iface = cumulus_bridge.BridgeMember('swp1')

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_symlink')
    def test_port_no_stp_enabled(self, mock_read_symlink, mock_exec, mock_read_from_sys):
        values2 = {('/sys/class/net/swp100/brport/bridge',): 'br100'}
        mock_read_symlink.side_effect = mod_args_generator(values2)
        values = {('bridge/stp_state',): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        self.iface = cumulus_bridge.BridgeMember('swp100')
        values = {
            'alternate': [],
            'designated': [],
            'disabled': ['br100'],
            'root': [],
            'backup': [],
            'oper_edge_port': [],
            'discarding': [],
            'forwarding': [],
            'network_port': []
        }
        _output = self.iface.stp.state
        for _category, _values in values.items():
            assert_equals([x.name for x in _output.get(_category)], _values)

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    def test_trunk_port_classic_driver(self, mock_exec,
                                       mock_read_from_sys):
        _results = {}
        values = {('bridge/stp_state',): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        self.iface = cumulus_bridge.BridgeMember('swp3')
        for i in ['root', 'backup', 'alternate', 'oper_edge_port',
                  'network_port', 'discarding', 'forwarding']:
            _results[i] = [x.name for x in self.iface.stp.state.get(i)]
        assert_equals(_results.get('root'), ['br0'])
        assert_equals(_results.get('backup'), ['br2'])
        assert_equals(_results.get('network_port'), ['br0'])
        assert_equals(_results.get('oper_edge_port'), ['br1'])
        assert_equals(_results.get('alternate'), [])
        assert_equals(_results.get('discarding'), ['br2'])
        assert_equals(sorted(_results.get('forwarding')), ['br0', 'br1'])

    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_get_native_vlan(self, mock_read_from_sys):
        # get untagged vlans. should be 9
        _filename = 'tests/test_netshowlib/brport_untagged_vlans.txt'
        vlanlist = open(_filename).readlines()
        values = {('bridge/stp_state', 'swp1', True): '2',
                  ('brport/untagged_vlans', 'swp1', False): vlanlist,
                  ('brport/vlans', 'swp1', True): True}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.native_vlan, ['9'])

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_vlans_new_driver_untagged(self, mock_read_from_sys):
        # get untagged vlans. should be 9
        _filename = 'tests/test_netshowlib/brport_untagged_vlans.txt'
        vlanlist = open(_filename).readlines()
        mock_read_from_sys.return_value = vlanlist
        assert_equals(self.iface.vlan_aware_vlan_list('untagged_vlans'),
                      ['9'])
        mock_read_from_sys.assert_called_with('brport/untagged_vlans',
                                              oneline=False)

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_get_vlans_new_driver(self, mock_read_from_sys):
        # Get all vlans of vlan aware port
        # vlans are 1-10,20-24,29-30,32,64,4092
        mock_read_from_sys.return_value = open(
            'tests/test_netshowlib/all_vlans.txt').readlines()
        vlan_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                     '20', '21', '22', '23', '24', '29', '30', '32',
                     '64', '4092']
        assert_equals(self.iface.vlan_aware_vlan_list('vlans'), vlan_list)
        mock_read_from_sys.assert_called_with('brport/vlans',
                                              oneline=False)


class TestCumulusBridge(object):

    def setup(self):
        self.iface = cumulus_bridge.Bridge('br0')

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_stp_mode(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/vlan_filtering', 'br0'): '1',
                  ('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        # CIST RSTP
        assert_equals(self.iface.stp.mode, 3)
        values = {('bridge/vlan_filtering', 'br0'): None,
                  ('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        # PSVT RSTP
        assert_equals(self.iface.stp.mode, 2)

    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_vlan_filtering(self, mock_read_from_sys):
        values = {('bridge/vlan_filtering', 'br0'): '1'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.vlan_filtering, 1)
        values = {('bridge/vlan_filtering', 'br0'): None}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.vlan_filtering, 0)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_root_port(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.stp.root_port, 'swp3')

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_is_root(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open(
            'tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.stp.is_root(), False)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_root_priority(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.stp.root_priority, 32768)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_bridge_priority(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.stp.bridge_priority, 32768)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_stp_property(self, mock_read_from_sys, mock_exec):
        # if stp_state is not 2
        assert_equals(isinstance(self.iface.stp, linux_bridge.KernelStpBridge), True)

        # if stp_state == 2
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(isinstance(self.iface.stp, cumulus_bridge.MstpctlStpBridge), True)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    @mock.patch('netshowlib.linux.bridge.os.listdir')
    def test_member_state(self, mock_listdir,
                          mock_read_from_sys, mock_exec):
        mock_listdir.return_value = ['swp3', 'swp4']
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0', True): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        _output = self.iface.stp.member_state
        for i in ['root', 'backup', 'alternate', 'oper_edge_port',
                  'network_port', 'discarding', 'forwarding']:
            self.__dict__[i] = [x.name for x in _output.get(i)]
        assert_equals(self.root, ['swp3'])
        assert_equals(self.backup, [])
        assert_equals(self.network_port, ['swp3'])
        assert_equals(self.oper_edge_port, [])
        assert_equals(self.alternate, ['swp4'])
        assert_equals(self.discarding, ['swp4'])
        assert_equals(self.forwarding, ['swp3'])

    @mock.patch('netshowlib.linux.common.os.listdir')
    def test_members(self, mock_listdir):
        mock_listdir.return_value = ['swp10.22', 'swp5', 'swp2s0.22']
        assert_equals(sorted(self.iface.members),
                      ['swp10', 'swp2s0', 'swp5'])
