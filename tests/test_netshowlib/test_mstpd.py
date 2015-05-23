# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
from netshowlib.cumulus import mstpd
import mock
from asserts import assert_equals
from nose.tools import set_trace


@mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
def test_cacheinfo(mock_exec):
    mock_exec.return_value = open('tests/test_netshowlib/mstpctl_showall').read()
    _output = mstpd.cacheinfo()
    assert_equals(sorted(_output.get('bridge').keys()), ['br0', 'br2'])
    assert_equals(sorted(_output.get('bridge').get('br0').get('ifaces').keys()),
                  ['swp3', 'swp4'])
    assert_equals(_output['bridge'].get('br0').get('ifaces').get('swp3').get('auto_edge_port'),
                  'yes')
    assert_equals(_output['bridge'].get('br0').get('designated_root'),
                  '8.000.00:02:00:00:00:02')
    # test getting data from iface structure
    assert_equals(sorted(_output['iface'].get('swp4').keys()),
                  ['br0', 'br2'])
    assert_equals(_output['iface'].get('swp3').get('br0').get('auto_edge_port'),
                  'yes')
