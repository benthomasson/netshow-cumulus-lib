""" Test Linux provider discovery
"""
# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
from netshowlib.linux.common import ExecCommandException
from netshowlib.linux import provider_discovery
import mock
import os
import sys
from asserts import assert_equals
from nose.tools import set_trace


def test_provider_check_file_exists():
    # disable this check if not running tests from tox
    assert_equals(os.path.exists(
        sys.prefix + '/share/netshow-lib/providers/cumulus'), True)


@mock.patch('netshowlib.linux.provider_discovery.common_mod.distro_info')
def test_check(mock_command):
    # Found linux OS
    # test with encoded string like in Python3 to ensure it gets decoded
    # properly
    mock_command.return_value =  {'ID': 'Cumulus Networks'}
    assert_equals(provider_discovery.check(), 'cumulus')
    # if for whatever reason provider check exec command fails
    mock_command.side_effect = ExecCommandException
    assert_equals(provider_discovery.check(), None)


@mock.patch('netshowlib.linux.provider_discovery.check')
def test_name_and_priority(mock_check):
    mock_check.return_value = 'cumulus'
    assert_equals(provider_discovery.name_and_priority(),
                  {'cumulus': '1'})
