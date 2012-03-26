#!/usr/bin/env python

"""

"""

__author__      = "Gary Buhrmaster"
__copyright__   = "Copyright 2012, Gary Buhrmaster"
__credits__     = ["Gary Buhrmaster"]
__version__     = "0.1"
__maintainer__  = "Gary Buhrmaster"
__email__       = "gary.buhrmaster@gmail.com"


from libhdhomerun import *

def test():

    # Test function

    # Note that most testing can only be done on a "live" environment,
    # so the unittest module is not used.

    # This may also be useful as example codes, although there should be
    # *no* presumption that this is good coding.  It was for testing only.

    import sys
    import re

    # Require the six compatibility library if running older python
    if sys.version_info < (3,):
        try:
            import six
        except Exception:
            print('This test suite was written for python3, and requires the python six compatibility library for older versions')
            sys.exit(1)

    def IPv4ToStr(ip):
        return '%d.%d.%d.%d' % ((ip>>24 & 0xff), (ip>>16 & 0xff), (ip>>8 & 0xff), (ip>>0 & 0xff))

    print ('Running tests...')

    # Create device
    device = hdhomerun_device_create(0, 0, 0, None)
    if device is None:
        print ('  Unable to create device')
        sys.exit(1)
    print ('  Created hdhomerun device')

    # Destroy device
    hdhomerun_device_destroy(device)
    print ('  Destroyed hdhomerun device')

    # Search for HDHR devices
    devices_discovered = (hdhomerun_discover_device_t * 64)()
    devices_found = hdhomerun_discover_find_devices_custom(0, HDHOMERUN_DEVICE_TYPE_TUNER, HDHOMERUN_DEVICE_ID_WILDCARD, devices_discovered, 64)
    if devices_found < 0:
        print ('  Error discovering devices')
    elif devices_found == 0:
        print ('  No devices found')
    else:
        print ('  %s hdhomerun devices found' % (devices_found))
        for i in range(devices_found):
            d = devices_discovered[i]
            print ('    Discovered device %X' % (d.device_id))
            device = hdhomerun_device_create(d.device_id, d.ip_addr, 0, None)
            if not device:
                print ('      Unable to create device %08X' % (d.device_id))
                continue
            print ('      Created device %08X' % (d.device_id))
            print ('        id:         %08X' % (hdhomerun_device_get_device_id(device)))
            print ('        ip:         %s' % (IPv4ToStr(hdhomerun_device_get_device_ip(device))))
            print ('        local ip:   %s' % (IPv4ToStr(hdhomerun_device_get_local_machine_addr(device))))
            model = hdhomerun_device_get_model_str(device).decode('UTF-8')
            print ('        model:      %s' % (model))
            print ('        tuners:     %i' % (d.tuner_count))
            version_str = ctypes.c_char_p()
            version_num = ctypes.c_int()
            hdhomerun_device_get_version(device, ctypes.byref(version_str), version_num)
            print ('        fwversion:  %s' % (version_str.value.decode('UTF-8')))
            location_str = ctypes.c_char_p()
            hdhomerun_device_get_lineup_location(device, ctypes.byref(location_str))
            print ('        lineup:     %s' % (location_str.value).decode('UTF-8'))
            features = ctypes.c_char_p()
            hdhomerun_device_get_supported(device, None, ctypes.byref(features))
            print ('        features:   %s' % (features.value.decode('UTF-8').rstrip('\r\n').replace('\n', '; ')))
            cablecard = re.search('cablecard', model)
            if cablecard:
                oob_status = hdhomerun_tuner_status_t()
                rc = hdhomerun_device_get_oob_status(device, None, oob_status)
                print ('        oob_lock:   %s' % (oob_status.lock_str.decode('UTF-8').rstrip('\r\n')))
                print ('        oob_ss:     %i' % (oob_status.signal_strength))
                print ('        oob_snr:    %i' % (oob_status.signal_to_noise_quality))
            for j in range(d.tuner_count):
                print ('        Examining tuner %i' % (j))
                rc = hdhomerun_device_set_tuner(device, j)
                if rc < 0:
                    print ('          Error setting tuner')
                    continue
                tuner_status = hdhomerun_tuner_status_t()
                rc = hdhomerun_device_get_tuner_status(device, None, tuner_status)
                print ('          channel:    %s' % (tuner_status.channel.decode('UTF-8').rstrip('\r\n')))
                print ('          lock:       %s' % (tuner_status.lock_str.decode('UTF-8').rstrip('\r\n')))
                print ('          present:    %i' % (tuner_status.signal_present))
                print ('          ss:         %i' % (tuner_status.signal_strength))
                print ('          snr:        %i' % (tuner_status.signal_to_noise_quality))
                print ('          seq:        %i' % (tuner_status.symbol_error_quality))
                print ('          bps:        %i' % (tuner_status.raw_bits_per_second))
                print ('          pps:        %i' % (tuner_status.packets_per_second))
                program = ctypes.c_char_p()
                hdhomerun_device_get_tuner_program(device, ctypes.byref(program))
                print ('          program:    %s' % (program.value.decode('UTF-8').rstrip('\r\n')))
                streaminfo = ctypes.c_char_p()
                hdhomerun_device_get_tuner_streaminfo(device, ctypes.byref(streaminfo))
                print ('          streaminfo: %s' % (streaminfo.value.decode('UTF-8').rstrip('\r\n').replace('\n', '; ')))
                filter = ctypes.c_char_p()
                hdhomerun_device_get_tuner_filter(device, ctypes.byref(filter))
                print ('          filter:     %s' % (filter.value.decode('UTF-8').rstrip('\r\n')))
                target = ctypes.c_char_p()
                hdhomerun_device_get_tuner_target(device, target)
                print ('          target:     %s' % (target.value.decode('UTF-8').rstrip('\r\n')))
                owner = ctypes.c_char_p()
                hdhomerun_device_get_tuner_lockkey_owner(device, owner)
                print ('          lock owner: %s' % (owner.value.decode('UTF-8').rstrip('\r\n')))
                if cablecard:
                    tuner_vstatus = hdhomerun_tuner_vstatus_t()
                    rc = hdhomerun_device_get_tuner_vstatus(device, None, tuner_vstatus)
                    print ('          vchannel:   %s' % (tuner_vstatus.vchannel.decode('UTF-8')))
                    print ('          name:       %s' % (tuner_vstatus.name.decode('UTF-8')))
                    print ('          auth:       %s' % (tuner_vstatus.auth.decode('UTF-8')))
                    print ('          cgms:       %s' % (tuner_vstatus.cgms.decode('UTF-8')))
                    print ('          not sub:    %i' % (tuner_vstatus.not_subscribed))
                    print ('          not avail:  %i' % (tuner_vstatus.not_available))
                    print ('          copy prot:  %i' % (tuner_vstatus.copy_protected))

            print ('')
            hdhomerun_device_destroy(device)

        # Request permission to scan channels (this can cause interruptions)
        scan_device = d.device_id
        scan_tuner = d.tuner_count - 1
        print ('The next tests perform a channel scan.  This requires control')
        print ('of a tuner.  If the tuner chosen is already in use (or will')
        print ('be used shortly by another process), this may disrupt ongoing')
        print ('captures.  The device-tuner to be used will be: %08X-%i' % (scan_device, scan_tuner))
        while True:
            if sys.version_info < (3,):
                ans = raw_input("Continue with channel scan? [y|N]: ")
            else:
                ans = input("Continue with channel scan? [y|N]: ")
            if not ans:
                ans = 'n'
            ans = ans.lower()
            if ans not in ['y', 'yes', 'n', 'no']:
                print ('please enter y or n.')
                continue
            if ans == 'n' or ans == 'no':
                ans = 'n'
                break
            if ans == 'y' or ans == 'yes':
                ans = 'y'
                break
        if ans == 'y': 
            print ('')
            device = hdhomerun_device_create(scan_device, 0, scan_tuner, None)
            if not device:
                print ('  Unable to create device for scanning (aborting scan)')
            else:
                lockkey = ctypes.c_char_p()
                rc = hdhomerun_device_tuner_lockkey_request(device, ctypes.byref(lockkey))
                if rc != 1:
                    print ('  Unable to lock tuner')
                    hdhomerun_device_destroy(device)
                else:
                    print ('  Beginning channel scan...')
                    channelmap = ctypes.c_char_p()
                    hdhomerun_device_get_tuner_channelmap(device, ctypes.byref(channelmap))
                    group = hdhomerun_channelmap_get_channelmap_scan_group(channelmap)
                    rc = hdhomerun_device_channelscan_init(device, group)
                    if rc == 1:
                        while 1:
                            scan_result = hdhomerun_channelscan_result_t()
                            rc = hdhomerun_device_channelscan_advance(device,ctypes.byref(scan_result))
                            if rc == 1:
                                print ('    Scanning frequency %i' % (scan_result.frequency))
                                rc = hdhomerun_device_channelscan_detect(device, ctypes.byref(scan_result))
                                if rc == 1:
                                    for i in range(scan_result.program_count):
                                        program = scan_result.programs[i]
                                        print ('      %s' % (program.program.decode('UTF-8')))
                                else:
                                    pass
                            else:
                                break
                    else:
                        print('  Unable to initialize scan')
                    hdhomerun_device_tuner_lockkey_release(device) 
                    hdhomerun_device_destroy(device)
                    print ('  Channel scan complete') 
   
    print ('') 
    print ('Tests completed')


if __name__ == '__main__':

    # If invoked as a main program, run tests on library, and HDHomeRun devices
    # (also a good debugging tool, although not definitive for anything)

    test()
