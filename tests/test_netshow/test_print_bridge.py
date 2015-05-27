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

class TestPrintBridgeMember(object):
    def setup(self):
        iface = cumulus_bridge.BridgeMember('swp22')
        self.piface = print_bridge.PrintBridgeMember(iface)

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
