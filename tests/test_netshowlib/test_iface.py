# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.cumulus.iface as cumulus_iface
from netshowlib.cumulus import asic
import mock
from asserts import assert_equals, mock_open_str, mod_args_generator
from nose.tools import set_trace

@mock.patch('netshowlib.cumulus.iface.os.path.exists')
def test_switch_asic(mock_path_exists):
    values ={'/etc/bcm.d/config.bcm': True}
    mock_path_exists.side_effect = mod_args_generator(values)
    _output = cumulus_iface.switch_asic()
    assert_equals(isinstance(_output, asic.BroadcomAsic), True)

class TestCumulusIface(object):

    def setup(self):
        self.iface = cumulus_iface.Iface('swp10')

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

    @mock.patch('netshowlib.cumulus.iface.Iface.is_phy')
    @mock.patch('netshowlib.cumulus.iface.os.path.exists')
    @mock.patch('netshowlib.cumulus.asic.BroadcomAsic.portspeed')
    def test_initial_speed(self, mock_port_speed, mock_path_exists,
                           mock_is_phy):
        mock_is_phy.return_value = True
        # initial speed cannot be found
        mock_path_exists.return_value = False
        assert_equals(self.iface.initial_speed(), None)
        # initial speed is broadcom
        values = {'/etc/bcm.d/config.bcm': True}
        mock_path_exists.side_effect = mod_args_generator(values)
        mock_port_speed.return_value = '1000'
        self.iface._asic = asic.BroadcomAsic()
        assert_equals(self.iface.initial_speed(), '1000')

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    @mock.patch('netshowlib.cumulus.iface.Iface.initial_speed')
    def test_speed(self, mock_initial_speed, mock_read_from_sys):
        # admin down
        values = {'carrier': None}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        mock_initial_speed.return_value = 'initial_speed'
        assert_equals(self.iface.speed, 'initial_speed')
        # carrier down, but admin up
        self.iface._speed = None
        values = {'carrier': '0', 'speed': '0'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.speed, '0')
        # carrier up, but admin up
        self.iface._speed = None
        values = {'carrier': '1', 'speed': '1000'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.speed, '1000')
