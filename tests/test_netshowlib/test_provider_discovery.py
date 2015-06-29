""" Test Linux provider discovery
"""
# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
from netshowlib.cumulus import provider_discovery
import mock
import os
import sys
from asserts import assert_equals, mock_open_str, mod_args_generator


def test_provider_check_file_exists():
    # disable this check if not running tests from tox
    assert_equals(os.path.exists(
        sys.prefix + '/share/netshow-lib/providers/cumulus'), True)


def test_check():
    # Found cumulus OS
    # test with encoded string like in Python3 to ensure it gets decoded
    # properly
    values = {('/etc/lsb-release', 'r'):
              open('tests/test_netshowlib/lsb-release.example')}
    with mock.patch(mock_open_str()) as mock_open:
        mock_open.side_effect = mod_args_generator(values)
        assert_equals(provider_discovery.check(), 'cumulus')


@mock.patch('netshowlib.cumulus.provider_discovery.check')
def test_name_and_priority(mock_check):
    mock_check.return_value = 'cumulus'
    assert_equals(provider_discovery.name_and_priority(),
                  {'cumulus': '1'})
