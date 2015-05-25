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
        assert_equals(self.piface.port_category, 'Access/L2')

