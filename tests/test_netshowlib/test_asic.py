# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
from netshowlib.cumulus import asic
import mock
from asserts import assert_equals, mock_open_str
from nose.tools import set_trace


class TestBroadcomAsic(object):

    def setup(self):
        self.asic = asic.BroadcomAsic()

    def test_name(self):
        assert_equals(self.asic.name, 'broadcom')

    @mock.patch('netshowlib.cumulus.asic.BroadcomAsic.portspeed')
    def test_connector_type(self, mock_portspeed):
        # sfp
        mock_portspeed.return_value = '1000'
        assert_equals(self.asic.connector_type('swp1'), 1)
        # sfp+
        mock_portspeed.return_value = '10000'
        assert_equals(self.asic.connector_type('swp2'), 2)
        # qsfp+
        mock_portspeed.return_value = '40000'
        assert_equals(self.asic.connector_type('swp3'), 3)

    def test_get_bcm_name_file_not_there(self):
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.side_effect = IOError
            assert_equals(self.asic.portname('swp10'), None)

    def test_bcm_name_swp2(self):
        porttab_file = open('tests/test_netshowlib/xe_porttab')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = porttab_file
            assert_equals(self.asic.portname('swp2'), 'xe1')

    def test_bcm_name_swp10(self):
        porttab_file = open('tests/test_netshowlib/xe_porttab')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = porttab_file
            assert_equals(self.asic.portname('swp10'), 'xe9')

    @mock.patch('netshowlib.cumulus.asic.BroadcomAsic.portname')
    def test_get_initial_speed_40g(self, mock_bcm_name):
        mock_bcm_name.return_value = 'xe56'
        xe_config_file = open('tests/test_netshowlib/config_xe.bcm')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = xe_config_file
            assert_equals(self.asic.portspeed('swp52'), '40000')

    @mock.patch('netshowlib.cumulus.asic.BroadcomAsic.portname')
    def test_get_initial_speed_10g(self, mock_bcm_name):
        mock_bcm_name.return_value = 'xe9'
        xe_config_file = open('tests/test_netshowlib/config_xe.bcm')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = xe_config_file
            assert_equals(self.asic.portspeed('swp10'), '10000')
