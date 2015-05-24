""" Linux Bond module tests
"""
# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.cumulus.bridge as cumulus_bridge
import netshowlib.linux.bridge as linux_bridge
import netshowlib.cumulus.bond as cumulus_bond
import netshowlib.cumulus.lacp as cumulus_lacp
import mock
from asserts import assert_equals
from nose.tools import set_trace


class TestLinuxBond(object):
    """ Linux bond tests """

    def setup(self):
        """ setup function """
        self.iface = cumulus_bond.Bond('bond0')

    @mock.patch('netshowlib.linux.common.read_file_oneline')
    def test_get_lacp_instance(self, mock_file_oneline):
        # test that calling iface.lacp and if iface is LACP
        # creates new Lacp instance
        mock_file_oneline.return_value = '802.3ad 4'
        assert_equals(isinstance(self.iface.lacp, cumulus_lacp.Lacp), True)
        # if bond is not using lacp
        mock_file_oneline.return_value = 'active-backup 1'
        assert_equals(self.iface.lacp, None)

    @mock.patch('netshowlib.linux.common.read_file_oneline')
    def test_get_stp(self, mock_file_oneline):
        # test stp call. returns mstpctl
        mock_file_oneline.return_value = '1'
        assert_equals(isinstance(self.iface.stp,
                                 cumulus_bridge.MstpctlStpBridgeMember), True)
        mock_file_oneline.assert_called_with(
            '/proc/sys/net/bridge/bridge-stp-user-space')
        # test stp call, returns kernel stp
        self.iface._stp = None
        mock_file_oneline.return_value = '0'
        assert_equals(isinstance(self.iface.stp,
                                 linux_bridge.KernelStpBridgeMember), True)

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_clag_eanble(self, mock_read_from_sys):
        mock_read_from_sys.return_value = '1'
        assert_equals(self.iface.clag_enable, '1')
        mock_read_from_sys.assert_called_with('bonding/clag_enable')
