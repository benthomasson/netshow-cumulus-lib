# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401

@mock.patch('netshowlib.linux.common.read_from_sys')
def test_vlan_aware_vlan_list_native(self, mock_read_from_sys):
        # get untagged vlans. should be 9
        _filename = 'tests/test_netshowlib/brport_untagged_vlans.txt'
        vlanlist = open(_filename).readlines()
        values = {('bridge/stp_state', 'swp1', True): '2',
                  ('brport/untagged_vlans', 'swp1', False): vlanlist,
                  ('brport/vlans', 'swp1', True): True}
        mock_read_from_sys.side_effect = mod_args_generator(values)
        assert_equals(self.iface.native_vlan, ['9'])


