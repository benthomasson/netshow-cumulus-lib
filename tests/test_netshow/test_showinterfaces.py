# http://pylint-messages.wikidot.com/all-codes
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

from asserts import assert_equals, mod_args_generator
from netshow.cumulus.show_interfaces import ShowInterfaces
import mock

@mock.patch('netshowlib.linux.iface.os.path.exists')
@mock.patch('netshowlib.linux.common.exec_command')
@mock.patch('netshowlib.linux.common.read_symlink')
@mock.patch('netshowlib.linux.common.read_from_sys')
@mock.patch('netshowlib.linux.iface.portname_list')
def test_showinterfaces(mock_portlist,
                        mock_read_from_sys,
                        mock_read_symlink,
                        mock_exec,
                        mock_os_path):
    mock_portlist.return_value = ['swp1', 'swp1.1',
                                  'swp3', 'swp2.1',
                                  'swp3', 'swp3.1',
                                  'bond0']
    values = {}
    values2 = {}
    values3 = {('lspci -nn',): '',
               ('/sbin/mstpctl showall',): '',
               ('/usr/sbin/lldpctl -f xml',): '<xml></xml>'}
    values4 = {('/sys/class/net/swp1/brif',): None}
    mock_read_from_sys.side_effect = mod_args_generator(values)
    mock_read_symlink.side_effect = mod_args_generator(values2)
    mock_exec.side_effect = mod_args_generator(values3)
    mock_os_path.side_effect = mod_args_generator(values4)
    results = {'interface': True}





