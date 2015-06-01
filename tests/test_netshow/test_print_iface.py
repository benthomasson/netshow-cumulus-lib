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
import mock
from asserts import assert_equals, mod_args_generator


class TestPrintIface(object):
    def setup(self):
        iface = cumulus_iface.Iface('swp22')
        self.piface = print_iface.PrintIface(iface)

    def test_connector_type(self):
        self.piface.iface._asic = {'asicname': 'ge1', 'initial_speed': '1000'}
        assert_equals(self.piface.connector_type, 'rj45')
        self.piface.iface._connector_type = None
        self.piface.iface._name = 'swp2s0'
        self.piface.iface._asic = {'asicname': 'xe1', 'initial_speed': '1000'}
        assert_equals(self.piface.connector_type, '4x10g')

    @mock.patch('netshowlib.cumulus.iface.Iface.is_mgmt')
    @mock.patch('netshowlib.cumulus.iface.Iface.is_svi')
    @mock.patch('netshowlib.linux.iface.Iface.is_loopback')
    def test_port_category(self, mock_linux_is_loopback,
                           mock_is_svi, mock_is_mgmt):
        # is svi
        mock_is_svi.return_value = True
        mock_is_mgmt.return_value = False
        assert_equals(self.piface.port_category, ('svi/l3'))
        assert_equals(mock_linux_is_loopback.call_count, 0)
        # is mgmt
        mock_is_svi.return_value = False
        mock_is_mgmt.return_value = True
        assert_equals(self.piface.port_category, ('mgmt'))
        assert_equals(mock_linux_is_loopback.call_count, 0)
        # use parent print category
        mock_is_mgmt.return_value = False
        mock_is_mgmt.return_value = False
        self.piface.port_category
        assert_equals(mock_linux_is_loopback.call_count, 1)

    @mock.patch('netshowlib.linux.iface.Iface.read_from_sys')
    def test_speed(self, mock_read_from_sys):
        values = {('speed',): '2000', ('carrier',): '1'}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        self.piface.iface._name = 'swp2s0'
        assert_equals(self.piface.speed, '2G(4x10g)')

    @mock.patch('netshowlib.cumulus.iface.Iface.is_phy')
    @mock.patch('netshowlib.linux.common.exec_command')
    def test_counter_summary(self, mock_exec_command,
                             mock_is_phy):
        mock_is_phy.return_value = False
        assert_equals(self.piface.counters_summary(), '')

        mock_is_phy.return_value = True
        mock_file = 'tests/test_netshowlib/ethtool_swp.txt'
        mock_exec_command.return_value = open(mock_file).read()
        _output = self.piface.counters_summary()
        _outputtable = _output.split('\n')
        assert_equals(_outputtable[0].split(), ['counters', 'tx', 'rx'])
        assert_equals(_outputtable[2].split(), ['errors', '20', '10'])
        assert_equals(_outputtable[3].split(), ['unicast', '400', '100'])
        assert_equals(_outputtable[4].split(), ['broadcast', '600', '200'])
        assert_equals(_outputtable[5].split(), ['multicast', '500', '300'])

    @mock.patch('netshow.linux.print_iface.PrintIface.cli_header')
    @mock.patch('netshow.linux.print_iface.PrintIface.ip_details')
    @mock.patch('netshow.linux.print_iface.PrintIface.lldp_details')
    @mock.patch('netshow.cumulus.print_iface.PrintIface.counters_summary')
    def test_cli_output(self, mock_counters, mock_lldp,
                        mock_ip_details, mock_cli_header):
        mock_counters.return_value = 'counters_output'
        mock_lldp.return_value = 'lldp_output'
        mock_ip_details.return_value = 'ip_details_output'
        mock_cli_header.return_value = 'cli_header_output'
        assert_equals([x  for x in self.piface.cli_output().split('\n') if x != ''],
                      ['cli_header_output', 'ip_details_output',
                       'counters_output', 'lldp_output'])
