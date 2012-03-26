#!/usr/bin/env python

import sys
import re
import collections
from optparse import OptionParser
from libhdhomerun import *
import ctypes
from utils import *

# Require the six compatibility library if running older python
if sys.version_info < (3,):
    try:
        import six
    except Exception:
        print('This test suite requires the python six compatibility library')
        sys.exit(1)

parser = OptionParser()
parser.add_option('--debug', action='store_true', default=False, dest='debug',
    help='Script Debugging')

(options, args) = parser.parse_args()

# Search for a useable HDHomeRun Prime device
devices_discovered = (hdhomerun_discover_device_t * 64)()
devices_found = hdhomerun_discover_find_devices_custom(0, HDHOMERUN_DEVICE_TYPE_TUNER, HDHOMERUN_DEVICE_ID_WILDCARD, devices_discovered, 64)
if devices_found < 0:
    print ('Error discovering HDHR devices')
    sys.exit(1)
elif devices_found == 0:
    print ('No HDHR devices found')
    sys.exit(1)
cablecard = 0
for i in range(devices_found):
    d = devices_discovered[i]
    device = hdhomerun_device_create(d.device_id, d.ip_addr, 0, None)
    if not device:
        continue
    if isHDHomeRunPrime(device):
        cablecard = 1
        # Check to see if we can get the virtual channel map
        # If not, try for another hdhomerun (probably no CC activated)
        vChannels = getVirtualChannels(device, options.debug)
        if len(vChannels) != 0:
            break
if not cablecard:
    print ('Unable to discover a HDHomeRun Prime')
if len(vChannels) == 0:
    print ('No virtual channels found (no HDHomeRun Prime reachable or cablecard not activated?)')

rc = hdhomerun_device_set_tuner(device, 2)
if rc != 1:
    print ('Unable to set tuner')

channels = getChannels(device, options.debug)

# Create a hash shortcut for quick checking of clear QAM channels
clearQAMChannels = {}
for c in channels:
    if (c.type == 0) and (c.virtual_major != 0) and (c.virtual_minor == 0):
        FM = str(int(c.frequency)) + ":" + str(int(c.program_number))
        clearQAMChannels[FM] = c

lastchannel= -1

vChannels.sort(key=lambda x:x.vchannel)

for c in vChannels:

    # For reasons I am sure make sense to someone, sometimes
    # the CableCARD map contains duplicate channel numbers.
    # Since we sort the map, just skip the duplicates
    if c.vchannel == lastchannel:
        continue

    lastchannel = c.vchannel

    rc = hdhomerun_device_set_tuner_vchannel(device, str(c.vchannel))
    if rc < 1:
        print('Info: Tuning failed for channel %s (possibly invalid channel)' % (c.vchannel))
        continue

    # Wait for lock (and get the status back)
    status = hdhomerun_tuner_status_t()
    rc = hdhomerun_device_wait_for_lock(device, status)
    if rc < 1:
        print('Info: Tuning and lock failed for channel %s (skipping channel)' % (c.vchannel))
        continue
    if not status.signal_present:
        print('Info: Tuning did not find signal for channel %s (skipping channel)' % (c.vchannel))
        continue

    # Get vstatus
    vstatus = hdhomerun_tuner_vstatus_t()
    rc = hdhomerun_device_get_tuner_vstatus(device, None, vstatus)
    if int(vstatus.vchannel) != c.vchannel:
        print('Info: Tuning failed to validate for channel %i (skipping channel)' % (c.vchannel))
        continue

    # Get program
    program_ctype = ctypes.c_char_p()
    rc = hdhomerun_device_get_tuner_program(device, ctypes.byref(program_ctype))
    if rc < 1:
        print('Info: Unable to acquire program number for channel %i (skipping channel)' % (c.vchannel))
        continue
    program = program_ctype.value

    FM = str(int(status.channel[4:]))+':'+str(int(program))

    if clearQAMChannels.has_key(FM):
        print ('vChannel %i is clear QAM, vname=%s, frequency=%i, program=%i, name=%s' % (c.vchannel, c.name, clearQAMChannels[FM].frequency, clearQAMChannels[FM].program_number, clearQAMChannels[FM].name))
    else:
        print ('vChannel %i is not available' % (c.vchannel))

