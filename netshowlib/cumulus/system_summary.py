"""
System Overview: Hardware info OS Distribution and CPU Architecture
for Cumulus Linux
"""
from netshowlib.linux import common as linux_common
from netshowlib.linux import system_summary as linux_system_summary
from cumulus_platform_info.cumulus_platform_info  import CumulusPlatformInfo


class SystemSummary(linux_system_summary.SystemSummary):
    """
    Class responsible for getting System HW summary info
    for Cumulus Linux
    """
    @property
    def platform_info(self):
        """
        :return hash of platform information based
        on the platform detect string
        """
        _platform_detect = linux_common.exec_command(
            '/usr/bin/platform-detect').strip()
        _platform_info = CumulusPlatformInfo(_platform_detect)
        return _platform_info.run()
