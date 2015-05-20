"""
module for mstpd functions
"""
from netshowlib.linux import common as linux_common
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import re

def cacheinfo():
    """
    :return hash of mstpd data. Logic is complicated. mstpctl needs to be JSON
    """
    # fails mccabe test..oh well!
    try:
        result = linux_common.exec_command('/sbin/mstpctl showall')
    except (ValueError, IOError):
        return {}
    bridgehash = {}
    is_bridge_info = False
    bridgename = None
    iface = None
    bridge_loc = None
    textio = StringIO(result)
    for line in textio:
        # if line is blank continue
        if len(line.strip()) <= 0:
            continue
        # if line as a ',' in it ignore it too. don't know how
        # parse these lines properly..so just ignore for now
        # again mstpctl output should be in JSON (filed a bug already)
        if len(line.split(',')) > 2:
            continue

        if bridgename:
            # if already parsing a bridge, and line starting
            # with BRIDGE is encountered, reset iface and bridgenam vars
            # get current line position and go back one line
            if line.startswith('BRIDGE'):
                bridgename = None
                iface = None
                pos = textio.tell()
                textio.seek(pos-1)
                continue

            # some magic code written by Jtoppins@cumulus
            # sets proper col dividers of the text output
            if is_bridge_info:
                next_col_at = 26
            else:
                next_col_at = 45

            # if line starts with the bridgename, then create
            # the stp hash associated with the bridge
            if line.split()[0] == bridgename:
                bridgehash[bridgename] = {}
                bridgehash[bridgename]['ifaces'] = {}
                is_bridge_info = True
                iface = None
                continue

            # else if its a line with the bridge member name
            # grab that and tell the parser that its time to
            # stop parsing bridge stp info and start parsing
            # bridge member stp info
            elif len(line.split()[0].split(':')) == 2:
                iface = line.split()[0].split(':')[1]
                is_bridge_info = False
                bridge_loc = None
                continue

            # this sets the correct hash location to write
            # the stp info. either the bridge or bridge member hash
            if not bridge_loc:
                if iface:
                    bridgehash[bridgename]['ifaces'][iface] = {}
                    bridge_loc = bridgehash[bridgename]['ifaces'][iface]
                else:
                    bridge_loc = bridgehash[bridgename]

            # col splitting magic. courteous of Jtoppins@cumulus
            if len(line) > 45:
                col = line[:next_col_at].strip().split()
                subkey = '_'.join(col[0:-1]).lower()
                value = col[-1]
                bridge_loc[subkey] = value.lower()
                col = line[next_col_at:].strip().split()
                subkey = '_'.join(col[0:-1]).lower()
                value = col[-1]
                bridge_loc[subkey] = value.lower()
            else:
                line = re.sub(r'\(.*\)', '', line)
                col = line.strip().split()
                subkey = '_'.join(col[0:-1]).lower()
                value = col[-1]
                bridge_loc[subkey] = value.lower()

        # this captures the beginning of a BRIDGE block
        # determine the bridge name and set the `bridgename var
        splitline = line.split()
        if splitline[0] == 'BRIDGE:':
            bridgename = splitline[1].strip(',')
            continue

    return bridgehash
