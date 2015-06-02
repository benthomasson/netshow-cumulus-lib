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

import netshow.cumulus.print_bond as print_bond
import netshowlib.cumulus.bond as cumulus_bond
import mock
from asserts import assert_equals, mod_args_generator


class TestPrintBondMember(object):
    def setup(self):
        iface = cumulus_bond.BondMember('swp22')
        self.piface = print_bond.PrintBondMember(iface)

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_speed(self, mock_read_sys):
        values = {('speed', ): '1000',
                  ('carrier',): '1'}
        self.piface.iface._asic = {'asicname': 'xe1', 'initial_speed': '10000'}
        mock_read_sys.side_effect = mod_args_generator(values)
        assert_equals(self.piface.speed, '1G(sfp)')
