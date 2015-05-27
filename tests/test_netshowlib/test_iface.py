# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.cumulus.iface as cumulus_iface
from netshowlib.cumulus import asic
from netshowlib.linux import common as linux_common
import mock
from asserts import assert_equals, mod_args_generator
from nose.tools import set_trace


@mock.patch('netshowlib.cumulus.iface.linux_common.exec_command')
def test_switch_asic(mock_exec_command):
    mock_exec_command.return_value = open('tests/test_netshowlib/lspci_output.txt', 'rb').read()
    instance = cumulus_iface.switch_asic()
    assert_equals(isinstance(instance, asic.BroadcomAsic), True)
    # no asic found
    mock_exec_command.side_effect = linux_common.ExecCommandException
    instance = cumulus_iface.switch_asic()
    assert_equals(instance, None)


class TestCumulusIface(object):

    def setup(self):
        self.asic = asic.BroadcomAsic()
        self.iface = cumulus_iface.Iface('swp10', swasic=self.asic)

    @mock.patch('netshowlib.linux.common.exec_command')
    @mock.patch('netshowlib.cumulus.iface.Iface.is_phy')
    def test_counters(self, mock_is_phy,
                      mock_exec_command):
        mock_is_phy.return_value = False
        assert_equals(self.iface.counters, None)
        mock_is_phy.return_value = True
        mock_file = 'tests/test_netshowlib/ethtool_swp.txt'
        mock_exec_command.return_value = open(mock_file).read()
        _output = self.iface.counters.rx
        assert_equals(_output, {'unicast': 100, 'multicast': 300,
                                'errors': 10, 'broadcast': 200})

    @mock.patch('netshowlib.linux.iface.Iface.is_subint')
    @mock.patch('netshowlib.linux.common.read_from_sys')
    def test_is_svi(self, mock_read_from_sys, mock_subint):
        # is not subint
        assert_equals(self.iface.is_svi(), False)

        # is subint but bridge parent does not have vlan_filtering
        self.iface._name = 'br10.100'
        mock_subint.return_value = True
        values = {('bridge/vlan_filtering', 'br10'): '0'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.is_svi(), False)

        # is subint but bridge parent does have vlan filtering
        self.iface._name = 'br10.100'
        mock_subint.return_value = True
        values = {('bridge/vlan_filtering', 'br10'): '1'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.is_svi(), True)

    def test_is_mgmt(self):
        # if starts with eth
        self.iface._name = 'eth22'
        assert_equals(self.iface.is_mgmt(), True)
        self.iface._name = 'eth0'
        assert_equals(self.iface.is_mgmt(), True)
        # starts with swp
        self.iface._name = 'swp10'
        assert_equals(self.iface.is_mgmt(), False)

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
    @mock.patch('netshowlib.cumulus.asic.BroadcomAsic.portspeed')
    def test_initial_speed(self, mock_port_speed,
                           mock_is_phy):
        mock_port_speed.return_value = None
        # initial speed cannot be found
        assert_equals(self.iface.initial_speed(), None)
        # initial speed is broadcom
        mock_port_speed.return_value = '1000'
        assert_equals(self.iface.initial_speed(), '1000')

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    @mock.patch('netshowlib.cumulus.iface.Iface.initial_speed')
    def test_speed(self, mock_initial_speed, mock_read_from_sys):
        # admin down
        values = {('carrier',): None}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        mock_initial_speed.return_value = 'initial_speed'
        assert_equals(self.iface.speed, 'initial_speed')
        # carrier down, but admin up
        self.iface._speed = None
        values = {('carrier',): '0', ('speed',): '0'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.speed, '0')
        # carrier up, but admin up
        self.iface._speed = None
        values = {('carrier',): '1', ('speed',): '1000'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.speed, '1000')
