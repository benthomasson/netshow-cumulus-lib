""" Linux LACP module tests
"""
# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.cumulus.lacp as cumulus_lacp
import mock
from asserts import assert_equals
from nose.tools import set_trace


class TestCumulusLacp(object):
    """ Cumulus LACP tests """

    def setup(self):
        """ setup function """
        self.lacp = cumulus_lacp.Lacp('bond0')

    @mock.patch('netshowlib.linux.common.read_file_oneline')
    def test_getting_lacp_bypass(self, mock_file_oneline):
        mock_file_oneline.return_value = '1'
        assert_equals(self.lacp.bypass, '1')
        mock_file_oneline.assert_called_with(
            '/sys/class/net/bond0/bonding/lacp_bypass_allowed')
