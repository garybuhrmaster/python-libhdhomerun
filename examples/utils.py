
def isHDHomeRunPrime(device, debug=False):
    "Returns True if the device is a HDHomeRun Prime"
    "Note: HDHomeRun Prime does not imply active CableCARD"

    import sys
    import re
    import libhdhomerun

    # Require the six compatibility library if running older python
    if sys.version_info < (3,):
        import six

    model_str = libhdhomerun.hdhomerun_device_get_model_str(device).decode('UTF-8')
    if debug:
        print ("Debug: isHDHomeRunPrime: model_str=%s" % (model_str))

    return re.search('cablecard', model_str)



def getVirtualChannels(device, debug=False):
    "Returns the CableCARD virtual channel list or an empty hash if error"
    "There is no API to get channel map, decodes the XML lineup"

    import sys
    import xml.etree.cElementTree
    import collections
    import libhdhomerun

    # Require the six compatibility library if running older python
    if sys.version_info < (3,):
        import six

    if sys.version_info < (3,):
        import urllib2 as urllib
    else:
        import urllib.request as urllib

    vChannels = []
    vChannelTuple = collections.namedtuple('vChannelTuple', 'vchannel name')

    def IPv4ToStr(ip):
        return '%d.%d.%d.%d' % ((ip>>24 & 0xff), (ip>>16 & 0xff), (ip>>8 & 0xff), (ip>>0 & 0xff))

    if not isHDHomeRunPrime(device, debug):
        if debug:
            print ('Debug: getVirtualChannels: HDHomeRun is not a prime')
        return vChannels

    HDHRIPv4 = IPv4ToStr(libhdhomerun.hdhomerun_device_get_device_ip(device)) 

    HDHRLineupURL = 'http://'+HDHRIPv4+'/lineup.xml'

    if debug:
        print ('Debug: getVirtualChannels: HDHomeRun Prime lineup url: %s' % (HDHRLineupURL))

    try:
        channelLineupXML = urllib.urlopen(HDHRLineupURL)
    except Exception as inst:
        if debug:
            print ('Debug: getVirtualChannels: unable to obtain lineup: %s' % (inst))
        return vChannels

    try:
        tree = xml.etree.cElementTree.parse(channelLineupXML)
    except Exception as inst:
        if debug:
            print ('Debug: getVirtualChannels: unable to parse lineup: %s' %(inst))
        return vChannels

    for node in tree.findall('Program'):
        GuideNumber = None
        GuideName = None
        for child in node.getchildren():
            if debug:
                print ('Debug: getVirtualChannels: child.tag=%s child.text=%s' % (child.tag, child.text))
            if (child.tag == 'GuideNumber') and (child.text.isdigit()):
                GuideNumber = int(child.text)
            if child.tag == 'GuideName':
                GuideName = child.text
        if (GuideName is not None) and (GuideNumber is not None):
            if debug:
                print ('Debug: getVirtualChannels: appending to list, vchannel=%i, name=%s' % (int(GuideNumber), GuideName))
            vChannels.append(vChannelTuple(vchannel=int(GuideNumber), name=GuideName))

    if debug:
        print ('Debug: getVirtualChannels: returning %i virtual channels' % (len(vChannels)))

    return vChannels


def getChannels(device, debug=False):
    "Returns the channel list or an empty hash if error"

    import sys
    import ctypes
    import collections
    import libhdhomerun

    # Require the six compatibility library if running older python
    if sys.version_info < (3,):
        import six

    channels = []
    channelTuple = collections.namedtuple('channelTuple', 'frequency program_number name type virtual_major virtual_minor')

    if debug:
        print ('Debug: getChannels: Beginning channel scan...')

    channelmap = ctypes.c_char_p()
    libhdhomerun.hdhomerun_device_get_tuner_channelmap(device, ctypes.byref(channelmap))
    group = libhdhomerun.hdhomerun_channelmap_get_channelmap_scan_group(channelmap)
    rc = libhdhomerun.hdhomerun_device_channelscan_init(device, group)
    if rc != 1:
        if debug:
            print ('Debug: getChannels: unable to initialize channelscan')
        return channels

    while 1:
        scan_result = libhdhomerun.hdhomerun_channelscan_result_t()
        rc = libhdhomerun.hdhomerun_device_channelscan_advance(device,ctypes.byref(scan_result))
        if rc == 1:
            if debug:
                print ('Debug: getChannels: Scanning frequency %i' % (scan_result.frequency))
            rc = libhdhomerun.hdhomerun_device_channelscan_detect(device, ctypes.byref(scan_result))
            if rc == 1:
                if debug:
                    print ('Debug: getChannels:  programs detected: %i' % (scan_result.program_count))
                for i in range(scan_result.program_count):
                    program = scan_result.programs[i]
                    if debug:
                        print ('Debug: getChannels:   %s' % (program.program.decode('UTF-8')))
                    channels.append(channelTuple(frequency=scan_result.frequency, name=program.name, program_number=program.program_number, type=program.type, virtual_major=program.virtual_major, virtual_minor=program.virtual_minor))
            else:
                if debug:
                    print ('Debug: getChannels:  detection failed')
                pass
        else:
            break

    if debug:
        print ('Debug: getChannels: Ending channel scan...')

    if debug:
        print ('Debug: getChannels: returning %i channels' % (len(channels)))

    return channels


