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
from asserts import assert_equals, mock_open_str, mod_args_generator
from nose.tools import set_trace


class TestCumulusBridge(object):

    def setup(self):
        self.iface = cumulus_bridge.Bridge('br0')

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
    def test_is_root(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0'): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.stp.is_root(), False)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_root_priority(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0'): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.stp.root_priority, 32768)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_bridge_priority(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0'): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.stp.bridge_priority, 32768)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_stp_property(self, mock_read_from_sys, mock_exec):
        # if stp_state is not 2
        assert_equals(isinstance(self.iface.stp, linux_bridge.KernelStpBridge), True)

        # if stp_state == 2
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0'): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(isinstance(self.iface.stp, cumulus_bridge.MstpctlStpBridge), True)

    @mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_member_state(self, mock_read_from_sys, mock_exec):
        mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
        values = {('bridge/stp_state', 'br0'): '2'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(sorted(self.iface.stp.member_state.keys()), ['swp3', 'swp4'])
        # test grabbing iface stp property
        assert_equals(self.iface.stp.member_state.get('swp4').get('port_id'), '8.002')

    @mock.patch('netshowlib.linux.common.os.listdir')
    def test_members(self, mock_listdir):
        mock_listdir.return_value = ['swp10.22', 'swp5', 'swp2s0.22']
        assert_equals(sorted(self.iface.members),
                      ['swp10', 'swp2s0', 'swp5'])
