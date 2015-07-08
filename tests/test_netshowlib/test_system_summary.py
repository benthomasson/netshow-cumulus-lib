"""
Test module  for getting system summary info for
Cumulus Linux
"""
# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
from netshowlib.cumulus import system_summary
import mock
from asserts import assert_equals
from nose.tools import set_trace


class TestSystemSummary(object):

    def setup(self):
        self.systemsummary = system_summary.SystemSummary()

    @mock.patch('netshowlib.cumulus.system_summary.linux_common.exec_command')
    @mock.patch('netshowlib.cumulus.system_summary.CumulusPlatformInfo')
    def test_platform_info(self, mock_cumulus_platform,
                           mock_exec):
        mock_exec.return_value = 'dell,s6000'
        instance = mock_cumulus_platform.return_value
        instance.run.return_value = 'Get Some Cool Output'
        assert_equals(self.systemsummary.platform_info, 'Get Some Cool Output')
        mock_cumulus_platform.assert_called_with('dell,s6000')
