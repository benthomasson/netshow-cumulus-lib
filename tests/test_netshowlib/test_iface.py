# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.cumulus.iface as cumulus_iface
import mock
from asserts import assert_equals, mock_open_str, mod_args_generator
from nose.tools import set_trace


class TestCumulusIface(object):

    def setup(self):
        self.iface = cumulus_iface.Iface('swp10')

    def test_get_bcm_name_file_not_there(self):
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.side_effect = IOError
            assert_equals(self.iface.bcm_name(), None)

    def test_is_phy(self):
        # if physical port
        self.iface._name = 'swp10'
        assert_equals(self.iface.is_phy(), True)
        # is another type of physical port
        self.iface._name = 'swp2s0'
        assert_equals(self.iface.is_phy(), True)
        # is not a physical port
        self.iface._name = 'swp10.100'
        assert_equals(self.iface.is_phy(), False)

    def test_bcm_name_swp2(self):
        self.iface._name = 'swp2'
        porttab_file = open('tests/test_netshowlib/xe_porttab')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = porttab_file
            assert_equals(self.iface.bcm_name(), 'xe1')

    def test_bcm_name_swp10(self):
        self.iface._name = 'swp10'
        porttab_file = open('tests/test_netshowlib/xe_porttab')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = porttab_file
            assert_equals(self.iface.bcm_name(), 'xe9')

    @mock.patch('netshowlib.cumulus.iface.Iface.is_phy')
    @mock.patch('netshowlib.cumulus.iface.Iface.bcm_name')
    def test_get_initial_speed_40g(self, mock_bcm_name, mock_phy):
        mock_phy.return_value = True
        mock_bcm_name.return_value = 'xe56'
        xe_config_file = open('tests/test_netshowlib/config_xe.bcm')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = xe_config_file
            assert_equals(self.iface.initial_speed, '40000')

    @mock.patch('netshowlib.cumulus.iface.Iface.is_phy')
    @mock.patch('netshowlib.cumulus.iface.Iface.bcm_name')
    def test_get_initial_speed_10g(self, mock_bcm_name, mock_phy):
        mock_phy.return_value = True
        mock_bcm_name.return_value = 'xe9'
        xe_config_file = open('tests/test_netshowlib/config_xe.bcm')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = xe_config_file
            assert_equals(self.iface.initial_speed, '10000')

    @mock.patch('netshowlib.cumulus.iface.Iface.is_phy')
    @mock.patch('netshowlib.cumulus.iface.Iface.bcm_name')
    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_speed(self, mock_read_from_sys,
                   mock_bcm_name, mock_phy):
        # link admin down
        self.iface._name = 'swp10'
        values = {'carrier': None}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        mock_phy.return_value = True
        mock_bcm_name.return_value = 'xe9'
        xe_config_file = open('tests/test_netshowlib/config_xe.bcm')
        with mock.patch(mock_open_str()) as mock_open:
            mock_open.return_value = xe_config_file
            assert_equals(self.iface.speed, '10000')

        # link not admin down, but carrier is down
        self.iface._speed = None
        values = {'carrier': '0', 'speed': '0'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.speed, '0')
        # links up and carrier up
        self.iface._speed = None
        values = {'carrier': '0', 'speed': '0'}
        values = {'carrier': '1', 'speed': '4000'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.speed, '4000')
