# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.cumulus.bridge as cumulus_bridge
import mock
from asserts import assert_equals, mock_open_str, mod_args_generator
from nose.tools import set_trace


class TestCumulusBridge(object):

    def setup(self):
        self.iface = cumulus_bridge.Bridge('br0')

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_is_svi(self, mock_read_from_sys):
        values = {'bridge/vlan_filtering': '1'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.vlan_filtering, 1)
        values = {'bridge/vlan_filtering': None}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.vlan_filtering, 0)

