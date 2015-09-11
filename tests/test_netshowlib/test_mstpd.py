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
import io

@mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
def test_cacheinfo_classic_bridge(mock_exec):
    mock_exec.return_value = io.open('tests/test_netshowlib/mstpctl_showall').read()
    _output = mstpd.cacheinfo()
    assert_equals(_output.get('bridge').get('br0').get('bridge_id'),  '8.000.00:02:00:00:00:0f')
    assert_equals(sorted(_output.get('bridge').keys()), ['br0', 'br1', 'br2'])
    assert_equals(sorted(_output.get('bridge').get('br0').get('ifaces').keys()),
                  ['swp3', 'swp4'])
    assert_equals(_output['bridge'].get('br0').get('ifaces').get('swp3').get('auto_edge_port'),
                  'yes')
    assert_equals(_output['bridge'].get('br1').get('designated_root'),
                  '8.000.00:02:00:00:00:0f')
    # test getting data from iface structure
    assert_equals(sorted(_output['iface'].get('swp4').keys()),
                  ['br0'])
    assert_equals(sorted(_output['iface'].get('swp4.1').keys()),
                  ['br1'])
    assert_equals(_output['iface'].get('swp3').get('br0').get('auto_edge_port'),
                  'yes')

    # test getting force_protocol_version data
    assert_equals(_output.get('bridge').get('br0').get('force_protocol_version'), 'rstp')

@mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
def test_cacheinfo_classic_bridge(mock_exec):
    mock_exec.return_value = io.open('tests/test_netshowlib/mstpctl_showall_vlanaware').read()
    _output = mstpd.cacheinfo()
    assert_equals(_output.get('bridge').get('bridge').get('bridge_id'), '8.000.44:38:39:ff:aa:11')


@mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
def test_cacheinfo_vlan_aware(mock_exec):
    mock_exec.return_value = io.open('tests/test_netshowlib/mstpctl_showall').read()
    _output = mstpd.cacheinfo()
    assert_equals(_output.get('bridge').get('br0').get('bridge_id'),  '8.000.00:02:00:00:00:0f')

@mock.patch('netshowlib.cumulus.mstpd.linux_common.exec_command')
def test_cacheinfo_no_stp(mock_exec):
    mock_exec.return_value = u''
    _output = mstpd.cacheinfo()
    assert_equals(_output.get('bridge'), {})
    assert_equals(_output.get('iface'), {})
