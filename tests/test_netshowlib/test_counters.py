# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
import netshowlib.linux.common as linux_common
from netshowlib.cumulus import counters
import mock
import io
from asserts import assert_equals


@mock.patch('netshowlib.linux.common.exec_command')
def test_counters_empty(mock_exec):
    mock_exec.side_effect = linux_common.ExecCommandException
    _output = counters.get_ethtool_output('swp1')
    assert_equals(_output, u'')


def test_get_physical_port_counters():
    mock_file = 'tests/test_netshowlib/ethtool_swp.txt'
    _output = counters.get_physical_port_counters(io.open(mock_file).read())
    assert_equals(_output, {
        'rx': {
            'errors': 10, 'unicast': 100,
            'multicast': 300, 'broadcast': 200
        },
        'tx': {
            'errors': 20, 'unicast': 400,
            'multicast': 500, 'broadcast': 600
        }
    })


@mock.patch('netshowlib.cumulus.counters.os.listdir')
@mock.patch('netshowlib.linux.common.exec_command')
def test_cacheinfo(mock_exec_command,
                   mock_os_listdir):
    mock_file = 'tests/test_netshowlib/ethtool_swp.txt'
    mock_exec_command.return_value = io.open(mock_file).read()
    mock_os_listdir.return_value = ['swp1', 'swp2s0',
                                    'swp2.2', 'swp3',
                                    'br0']
    _output = counters.cacheinfo()
    assert_equals(sorted(_output.keys()), ['swp1', 'swp2s0', 'swp3'])
    # single interface
    _output = counters.cacheinfo('swp2')
    assert_equals(sorted(_output.keys()), ['swp2'])


class TestCumulusCounters(object):

    def setup(self):
        self.counters = counters.Counters(name='swp10', cache=None)

    @mock.patch('netshowlib.cumulus.counters.os.listdir')
    @mock.patch('netshowlib.linux.common.exec_command')
    def test_run(self, mock_exec, mock_listdir):
        mock_file = 'tests/test_netshowlib/ethtool_swp.txt'
        mock_exec.return_value = io.open(mock_file).read()
        mock_listdir.return_value = ['swp1', 'swp2s0',
                                     'swp2.2', 'swp3', 'swp10',
                                     'br0']
        self.counters.run()
        assert_equals(self.counters.rx.get('unicast'), 100)
        assert_equals(self.counters.tx.get('errors'), 20)
        assert_equals(self.counters.total_rx, 600)
        assert_equals(self.counters.total_tx, 1500)
        assert_equals(self.counters.total_err, 30)

    @mock.patch('netshowlib.cumulus.counters.os.listdir')
    @mock.patch('netshowlib.linux.common.exec_command')
    def test_all(self, mock_exec, mock_listdir):
        mock_file = 'tests/test_netshowlib/ethtool_swp.txt'
        mock_exec.return_value = io.open(mock_file).read()
        mock_listdir.return_value = ['swp1', 'swp2s0',
                                     'swp2.2', 'swp3', 'swp10',
                                     'br0']
        self.counters.run()
        _output = self.counters.all
        assert_equals(_output['rx'].get('unicast'), 100)
        assert_equals(_output['tx'].get('errors'), 20)
