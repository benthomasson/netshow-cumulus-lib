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

import netshow.cumulus.print_iface as print_iface
import netshowlib.cumulus.iface as cumulus_iface
import netshowlib.cumulus.asic as cumulus_asic
import mock
from asserts import assert_equals, mod_args_generator
from nose.tools import set_trace


class TestPrintIface(object):
    def setup(self):

        iface = cumulus_iface.Iface('swp22',
                                    swasic=cumulus_asic.BroadcomAsic())
        self.piface = print_iface.PrintIface(iface)

    @mock.patch('netshowlib.cumulus.iface.switch_asic')
    @mock.patch('netshowlib.cumulus.asic.BroadcomAsic.connector_type')
    def test_connector_type(self, mock_connector, mock_asic):
        mock_asic.return_value = cumulus_asic.BroadcomAsic()
        mock_connector.return_value = None
        assert_equals(self.piface.connector_type, None)
        mock_connector.return_value = 1
        assert_equals(self.piface.connector_type, 'rj45')
        mock_connector.return_value = 2
        assert_equals(self.piface.connector_type, 'sfp')
        mock_connector.return_value = 3
        assert_equals(self.piface.connector_type, 'qsfp')
        self.piface.iface._name = 'swp2s0'
        assert_equals(self.piface.connector_type, '4x10g')

