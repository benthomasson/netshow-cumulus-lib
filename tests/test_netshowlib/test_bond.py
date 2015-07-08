""" Cumulus Bond module tests
"""
# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.cumulus.bond as cumulus_bond
import io
import mock
from asserts import assert_equals, mod_args_generator, mock_open_str


class TestBondMember(object):
    """ Linux bondmember tests """

    def setup(self):
        """ setup function """
        self.iface = cumulus_bond.BondMember('swp1')

    @mock.patch('netshowlib.cumulus.asic.linux_common.exec_command')
    def test_connector_type(self, mock_exec):
        mock_exec.return_value = io.open('tests/test_netshowlib/lspci_output.txt', 'rb').read()
        values = {
            ('/var/lib/cumulus/porttab',): io.open('tests/test_netshowlib/xe_porttab'),
            ('/etc/bcm.d/config.bcm',): io.open('tests/test_netshowlib/config_xe.bcm')
        }
        with mock.patch('io.open') as mock_open:
            mock_open.side_effect = mod_args_generator(values)
            assert_equals(self.iface.connector_type, 2)
