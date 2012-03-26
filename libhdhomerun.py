"""

libhdhomerun

libhdhomerun is a python module for accessing the SiliconDust
shared library using python ctypes foreign function technology.

Copyright (c) 2012 by Gary Buhrmaster <gary.buhrmaster@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

__author__      = "Gary Buhrmaster"
__copyright__   = "Copyright 2012, Gary Buhrmaster"
__credits__     = ["Gary Buhrmaster"]
__license__     = "Apache License 2.0"
__version__     = "0.1.0"
__maintainer__  = "Gary Buhrmaster"
__email__       = "gary.buhrmaster@gmail.com"
__status__      = "Beta"
__title__       = "libhdhomerun"

import ctypes
import sys

HDHOMERUN_STATUS_COLOR_NEUTRAL            = 0xFFFFFFFF
HDHOMERUN_STATUS_COLOR_RED                = 0xFFFF0000
HDHOMERUN_STATUS_COLOR_YELLOW             = 0xFFFFFF00
HDHOMERUN_STATUS_COLOR_GREEN              = 0xFF00C000
HDHOMERUN_CHANNELSCAN_MAX_PROGRAM_COUNT   = 64
HDHOMERUN_CHANNELSCAN_PROGRAM_NORMAL      = 0
HDHOMERUN_CHANNELSCAN_PROGRAM_NODATA      = 1
HDHOMERUN_CHANNELSCAN_PROGRAM_CONTROL     = 2
HDHOMERUN_CHANNELSCAN_PROGRAM_ENCRYPTED   = 3
HDHOMERUN_DEVICE_TYPE_WILDCARD            = 0xFFFFFFFF
HDHOMERUN_DEVICE_TYPE_TUNER               = 0x00000001
HDHOMERUN_DEVICE_ID_WILDCARD              = 0xFFFFFFFF
HDHOMERUN_DEVICE_MAX_TUNE_TO_LOCK_TIME    = 1500
HDHOMERUN_DEVICE_MAX_LOCK_TO_DATA_TIME    = 2000
HDHOMERUN_DEVICE_MAX_TUNE_TO_DATA_TIME    = (HDHOMERUN_DEVICE_MAX_TUNE_TO_LOCK_TIME + HDHOMERUN_DEVICE_MAX_LOCK_TO_DATA_TIME)

class hdhomerun_device_t(ctypes.Structure):
    pass

class hdhomerun_debug_t(ctypes.Structure):
    pass

class hdhomerun_control_sock_t(ctypes.Structure):
    pass

class hdhomerun_video_sock_t(ctypes.Structure):
    pass

class hdhomerun_video_stats_t(ctypes.Structure):
    _fields_ = [
                ("packet_count", ctypes.c_uint32),
                ("network_error_count", ctypes.c_uint32),
                ("transport_error_count", ctypes.c_uint32),
                ("sequence_error_count", ctypes.c_uint32),
                ("overflow_error_count", ctypes.c_uint32)
               ]

class hdhomerun_tuner_status_t(ctypes.Structure):
    _fields_ = [
                ("channel", ctypes.c_char * 32),
                ("lock_str", ctypes.c_char * 32),
                ("signal_present", ctypes.c_int32),
                ("lock_supported", ctypes.c_int32),
                ("lock_unsupported", ctypes.c_int32),
                ("signal_strength", ctypes.c_uint32),
                ("signal_to_noise_quality", ctypes.c_uint32),
                ("symbol_error_quality", ctypes.c_uint32),
                ("raw_bits_per_second", ctypes.c_uint32),
                ("packets_per_second", ctypes.c_uint32)
               ]

class hdhomerun_tuner_vstatus_t(ctypes.Structure):
    _fields_ = [
                ("vchannel", ctypes.c_char * 32),
                ("name", ctypes.c_char * 32),
                ("auth", ctypes.c_char * 32),
                ("cci", ctypes.c_char * 32),
                ("cgms", ctypes.c_char * 32),
                ("not_subscribed", ctypes.c_int32),
                ("not_available", ctypes.c_int32),
                ("copy_protected", ctypes.c_int32)
               ]

class hdhomerun_channelscan_program_t(ctypes.Structure):
    _fields_ = [
                ("program", ctypes.c_char * 64),
                ("program_number", ctypes.c_uint16),
                ("virtual_major", ctypes.c_uint16),
                ("virtual_minor", ctypes.c_uint16),
                ("type", ctypes.c_uint16),
                ("name", ctypes.c_char * 32)
               ]

class hdhomerun_channelscan_result_t(ctypes.Structure):
    _fields_ = [
                ("channel_str", ctypes.c_char * 64),
                ("channelmap", ctypes.c_uint32),
                ("frequency", ctypes.c_uint32),
                ("status", hdhomerun_tuner_status_t),
                ("program_count", ctypes.c_int32),
                ("programs", hdhomerun_channelscan_program_t * HDHOMERUN_CHANNELSCAN_MAX_PROGRAM_COUNT),
                ("transport_stream_id_detected", ctypes.c_int32),
                ("transport_stream_id", ctypes.c_uint16)
               ]
       
class hdhomerun_plotsample_t(ctypes.Structure):
    _fields_ = [
                ("real", ctypes.c_int16),
                ("imag", ctypes.c_int16)
               ]

class hdhomerun_discover_device_t(ctypes.Structure):
    _fields_ = [
                ("ip_addr", ctypes.c_uint32),
                ("device_type", ctypes.c_uint32),
                ("device_id", ctypes.c_uint32),
                ("tuner_count", ctypes.c_uint8)
               ]

__libs = {}

# Due to platform/compiler differences, the shared library
# may have differing names on differing platforms.  Try the
# alternatives on the specified platforms (POSIX is the default)
__lib_name_formats = ['lib%s.so', 'lib%s.sl', '%s.so', '%s.sl']
if (sys.platform == 'darwin'): __lib_name_formats = ['lib%s.dylib', 'lib%s.so', 'lib%s.bundle', '%s.dylib', '%s.so', '%s.bundle', '%s']
if (sys.platform == 'win32') or (sys.platform == 'cygwin'): __lib_name_formats = ['lib%s.dll', '%s.dll', '%slib.dll']

__libs['hdhomerun'] = None

__lib_errors = []

for __lib_name in __lib_name_formats:
    __libname = __lib_name % ('hdhomerun')
    try:
        __libs['hdhomerun'] = ctypes.CDLL(__libname)
        break
    except Exception as inst:
        inst = 'Attempting to load %s: ' % (__libname) + str(inst)
        __lib_errors.append(inst)

# Raise the error for failing to load library, displaying
# all the accumlated places that were searched....
if __libs['hdhomerun'] is None:
    __lib_load_error = ('; '.join(__lib_errors))
    raise OSError(__lib_load_error)

# Define functions (somewhat) safely
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_create'):
    hdhomerun_device_create = __libs['hdhomerun'].hdhomerun_device_create
    hdhomerun_device_create.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint, ctypes.POINTER(hdhomerun_debug_t)] 
    hdhomerun_device_create.restype = ctypes.POINTER(hdhomerun_device_t)
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_create_from_str'):
    hdhomerun_device_create_from_str = __libs['hdhomerun'].hdhomerun_device_create_from_str
    hdhomerun_device_create_from_str.argtypes = [ctypes.c_char_p, ctypes.POINTER(hdhomerun_debug_t)]
    hdhomerun_device_create_from_str.restype = ctypes.POINTER(hdhomerun_device_t)
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_destroy'):
    hdhomerun_device_destroy = __libs['hdhomerun'].hdhomerun_device_destroy
    hdhomerun_device_destroy.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_destroy.restype = None
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_name'):
    hdhomerun_device_get_name = __libs['hdhomerun'].hdhomerun_device_get_name
    hdhomerun_device_get_name.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_name.restype = ctypes.c_char_p
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_device_id'):
    hdhomerun_device_get_device_id = __libs['hdhomerun'].hdhomerun_device_get_device_id
    hdhomerun_device_get_device_id.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_device_id.restype = ctypes.c_uint32
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_device_ip'):
    hdhomerun_device_get_device_ip = __libs['hdhomerun'].hdhomerun_device_get_device_ip
    hdhomerun_device_get_device_ip.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_device_ip.restype = ctypes.c_uint32
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_device_id_requested'):
    hdhomerun_device_get_device_id_requested = __libs['hdhomerun'].hdhomerun_device_get_device_id_requested
    hdhomerun_device_get_device_id_requested.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_device_id_requested.restype = ctypes.c_uint32
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_device_ip_requested'):
    hdhomerun_device_get_device_ip_requested = __libs['hdhomerun'].hdhomerun_device_get_device_ip_requested
    hdhomerun_device_get_device_ip_requested.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_device_ip_requested.restype = ctypes.c_uint32
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner'):
    hdhomerun_device_get_tuner = __libs['hdhomerun'].hdhomerun_device_get_tuner
    hdhomerun_device_get_tuner.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_tuner.restype = ctypes.c_uint
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_device'):
    hdhomerun_device_set_device = __libs['hdhomerun'].hdhomerun_device_set_device
    hdhomerun_device_set_device.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_uint32, ctypes.c_uint32]
    hdhomerun_device_set_device.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_tuner'):
    hdhomerun_device_set_tuner = __libs['hdhomerun'].hdhomerun_device_set_tuner
    hdhomerun_device_set_tuner.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_uint]
    hdhomerun_device_set_tuner.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_tuner_from_str'):
    hdhomerun_device_set_tuner_from_str = __libs['hdhomerun'].hdhomerun_device_set_tuner_from_str
    hdhomerun_device_set_tuner_from_str.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_tuner_from_str.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_local_machine_addr'):
    hdhomerun_device_get_local_machine_addr = __libs['hdhomerun'].hdhomerun_device_get_local_machine_addr
    hdhomerun_device_get_local_machine_addr.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_local_machine_addr.restype = ctypes.c_uint32
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_status'):
    hdhomerun_device_get_tuner_status = __libs['hdhomerun'].hdhomerun_device_get_tuner_status
    hdhomerun_device_get_tuner_status.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(hdhomerun_tuner_status_t)]
    hdhomerun_device_get_tuner_status.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_vstatus'):
    hdhomerun_device_get_tuner_vstatus = __libs['hdhomerun'].hdhomerun_device_get_tuner_vstatus
    hdhomerun_device_get_tuner_vstatus.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(hdhomerun_tuner_vstatus_t)]
    hdhomerun_device_get_tuner_vstatus.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_streaminfo'):
    hdhomerun_device_get_tuner_streaminfo = __libs['hdhomerun'].hdhomerun_device_get_tuner_streaminfo
    hdhomerun_device_get_tuner_streaminfo.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_tuner_streaminfo.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_channel'):
    hdhomerun_device_get_tuner_channel = __libs['hdhomerun'].hdhomerun_device_get_tuner_channel
    hdhomerun_device_get_tuner_channel.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_tuner_channel.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_vchannel'):
    hdhomerun_device_get_tuner_vchannel = __libs['hdhomerun'].hdhomerun_device_get_tuner_vchannel
    hdhomerun_device_get_tuner_vchannel.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_tuner_vchannel.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_channelmap'):
    hdhomerun_device_get_tuner_channelmap = __libs['hdhomerun'].hdhomerun_device_get_tuner_channelmap
    hdhomerun_device_get_tuner_channelmap.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_tuner_channelmap.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_filter'):
    hdhomerun_device_get_tuner_filter = __libs['hdhomerun'].hdhomerun_device_get_tuner_filter
    hdhomerun_device_get_tuner_filter.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_tuner_filter.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_program'):
    hdhomerun_device_get_tuner_program = __libs['hdhomerun'].hdhomerun_device_get_tuner_program
    hdhomerun_device_get_tuner_program.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_tuner_program.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_target'):
    hdhomerun_device_get_tuner_target = __libs['hdhomerun'].hdhomerun_device_get_tuner_target
    hdhomerun_device_get_tuner_target.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_tuner_target.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_plotsample'):
    hdhomerun_device_get_tuner_plotsample = __libs['hdhomerun'].hdhomerun_device_get_tuner_plotsample
    hdhomerun_device_get_tuner_plotsample.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.POINTER(hdhomerun_plotsample_t)), ctypes.POINTER(ctypes.c_size_t)]
    hdhomerun_device_get_tuner_plotsample.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_oob_status'):
    hdhomerun_device_get_oob_status = __libs['hdhomerun'].hdhomerun_device_get_oob_status
    hdhomerun_device_get_oob_status.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(hdhomerun_tuner_status_t)]
    hdhomerun_device_get_oob_status.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_oob_plotsample'):
    hdhomerun_device_get_oob_plotsample = __libs['hdhomerun'].hdhomerun_device_get_oob_plotsample
    hdhomerun_device_get_oob_plotsample.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.POINTER(hdhomerun_plotsample_t)), ctypes.POINTER(ctypes.c_size_t)]
    hdhomerun_device_get_oob_plotsample.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_lockkey_owner'):
    hdhomerun_device_get_tuner_lockkey_owner = __libs['hdhomerun'].hdhomerun_device_get_tuner_lockkey_owner
    hdhomerun_device_get_tuner_lockkey_owner.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_tuner_lockkey_owner.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_ir_target'):
    hdhomerun_device_get_ir_target = __libs['hdhomerun'].hdhomerun_device_get_ir_target
    hdhomerun_device_get_ir_target.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_ir_target.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_lineup_location'):
    hdhomerun_device_get_lineup_location = __libs['hdhomerun'].hdhomerun_device_get_lineup_location
    hdhomerun_device_get_lineup_location.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_lineup_location.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_version'):
    hdhomerun_device_get_version = __libs['hdhomerun'].hdhomerun_device_get_version
    hdhomerun_device_get_version.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_int32)]
    hdhomerun_device_get_version.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_supported'):
    hdhomerun_device_get_supported = __libs['hdhomerun'].hdhomerun_device_get_supported
    hdhomerun_device_get_supported.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_supported.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_status_ss_color'):
    hdhomerun_device_get_tuner_status_ss_color = __libs['hdhomerun'].hdhomerun_device_get_tuner_status_ss_color
    hdhomerun_device_get_tuner_status_ss_color.argtypes = [ctypes.POINTER(hdhomerun_tuner_status_t)]
    hdhomerun_device_get_tuner_status_ss_color.restype = ctypes.c_uint32
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_status_snq_color'):
    hdhomerun_device_get_tuner_status_snq_color = __libs['hdhomerun'].hdhomerun_device_get_tuner_status_snq_color
    hdhomerun_device_get_tuner_status_snq_color.argtypes = [ctypes.POINTER(hdhomerun_tuner_status_t)]
    hdhomerun_device_get_tuner_status_snq_color.restype = ctypes.c_uint32
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_tuner_status_seq_color'):
    hdhomerun_device_get_tuner_status_seq_color = __libs['hdhomerun'].hdhomerun_device_get_tuner_status_seq_color
    hdhomerun_device_get_tuner_status_seq_color.argtypes = [ctypes.POINTER(hdhomerun_tuner_status_t)]
    hdhomerun_device_get_tuner_status_seq_color.restype = ctypes.c_uint32
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_model_str'):
    hdhomerun_device_get_model_str = __libs['hdhomerun'].hdhomerun_device_get_model_str
    hdhomerun_device_get_model_str.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_model_str.restype = ctypes.c_char_p
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_tuner_channel'):
    hdhomerun_device_set_tuner_channel = __libs['hdhomerun'].hdhomerun_device_set_tuner_channel
    hdhomerun_device_set_tuner_channel.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_tuner_channel.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_tuner_vchannel'):
    hdhomerun_device_set_tuner_vchannel = __libs['hdhomerun'].hdhomerun_device_set_tuner_vchannel
    hdhomerun_device_set_tuner_vchannel.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_tuner_vchannel.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_tuner_filter'):
    hdhomerun_device_set_tuner_filter = __libs['hdhomerun'].hdhomerun_device_set_tuner_filter
    hdhomerun_device_set_tuner_filter.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_tuner_filter.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_tuner_program'):
    hdhomerun_device_set_tuner_program = __libs['hdhomerun'].hdhomerun_device_set_tuner_program
    hdhomerun_device_set_tuner_program.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_tuner_program.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_tuner_target'):
    hdhomerun_device_set_tuner_target = __libs['hdhomerun'].hdhomerun_device_set_tuner_target
    hdhomerun_device_set_tuner_target.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_tuner_target.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_lineup_location'):
    hdhomerun_device_set_lineup_location = __libs['hdhomerun'].hdhomerun_device_set_lineup_location
    hdhomerun_device_set_lineup_location.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_lineup_location.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_sys_dvbc_modulation'):
    hdhomerun_device_set_sys_dvbc_modulation = __libs['hdhomerun'].hdhomerun_device_set_sys_dvbc_modulation
    hdhomerun_device_set_sys_dvbc_modulation.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_sys_dvbc_modulation.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_ir_target'):
    hdhomerun_device_set_ir_target = __libs['hdhomerun'].hdhomerun_device_set_ir_target
    hdhomerun_device_set_ir_target.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_set_ir_target.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_var'):
    hdhomerun_device_get_var = __libs['hdhomerun'].hdhomerun_device_get_var
    hdhomerun_device_get_var.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_get_var.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_set_var'):
    hdhomerun_device_set_var = __libs['hdhomerun'].hdhomerun_device_set_var
    hdhomerun_device_set_var.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_set_var.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_tuner_lockkey_request'):
    hdhomerun_device_tuner_lockkey_request = __libs['hdhomerun'].hdhomerun_device_tuner_lockkey_request
    hdhomerun_device_tuner_lockkey_request.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(ctypes.c_char_p)]
    hdhomerun_device_tuner_lockkey_request.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_tuner_lockkey_release'):
    hdhomerun_device_tuner_lockkey_release = __libs['hdhomerun'].hdhomerun_device_tuner_lockkey_release
    hdhomerun_device_tuner_lockkey_release.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_tuner_lockkey_release.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_tuner_lockkey_force'):
    hdhomerun_device_tuner_lockkey_force = __libs['hdhomerun'].hdhomerun_device_tuner_lockkey_force
    hdhomerun_device_tuner_lockkey_force.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_tuner_lockkey_force.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_tuner_lockkey_use_value'):
    hdhomerun_device_tuner_lockkey_use_value = __libs['hdhomerun'].hdhomerun_device_tuner_lockkey_use_value
    hdhomerun_device_tuner_lockkey_use_value.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_uint32]
    hdhomerun_device_tuner_lockkey_use_value.restype = None
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_wait_for_lock'):
    hdhomerun_device_wait_for_lock = __libs['hdhomerun'].hdhomerun_device_wait_for_lock
    hdhomerun_device_wait_for_lock.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(hdhomerun_tuner_status_t)]
    hdhomerun_device_wait_for_lock.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_stream_start'):
    hdhomerun_device_stream_start = __libs['hdhomerun'].hdhomerun_device_stream_start
    hdhomerun_device_stream_start.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_stream_start.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_stream_recv'):
    hdhomerun_device_stream_recv = __libs['hdhomerun'].hdhomerun_device_stream_recv
    hdhomerun_device_stream_recv.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_stream_recv.restype = ctypes.c_uint8
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_stream_flush'):
    hdhomerun_device_stream_flush = __libs['hdhomerun'].hdhomerun_device_stream_flush
    hdhomerun_device_stream_flush.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_stream_flush.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_stream_stop'):
    hdhomerun_device_stream_stop = __libs['hdhomerun'].hdhomerun_device_stream_stop
    hdhomerun_device_stream_stop.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_stream_stop.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_channelscan_init'):
    hdhomerun_device_channelscan_init = __libs['hdhomerun'].hdhomerun_device_channelscan_init
    hdhomerun_device_channelscan_init.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.c_char_p]
    hdhomerun_device_channelscan_init.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_channelscan_advance'):
    hdhomerun_device_channelscan_advance = __libs['hdhomerun'].hdhomerun_device_channelscan_advance
    hdhomerun_device_channelscan_advance.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(hdhomerun_channelscan_result_t)]
    hdhomerun_device_channelscan_advance.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_channelscan_detect'):
    hdhomerun_device_channelscan_detect = __libs['hdhomerun'].hdhomerun_device_channelscan_detect
    hdhomerun_device_channelscan_detect.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(hdhomerun_channelscan_result_t)]
    hdhomerun_device_channelscan_detect.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_channelscan_get_progress'):
    hdhomerun_device_channelscan_get_progress = __libs['hdhomerun'].hdhomerun_device_channelscan_get_progress
    hdhomerun_device_channelscan_get_progress.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_channelscan_get_progress.restype = ctypes.c_uint8
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_control_sock'):
    hdhomerun_device_get_control_sock = __libs['hdhomerun'].hdhomerun_device_get_control_sock
    hdhomerun_device_get_control_sock.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_control_sock.restype = ctypes.POINTER(hdhomerun_control_sock_t)
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_video_sock'):
    hdhomerun_device_get_video_sock = __libs['hdhomerun'].hdhomerun_device_get_video_sock
    hdhomerun_device_get_video_sock.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_get_video_sock.restype = ctypes.POINTER(hdhomerun_video_sock_t)
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_debug_print_video_stats'):
    hdhomerun_device_debug_print_video_stats = __libs['hdhomerun'].hdhomerun_device_debug_print_video_stats
    hdhomerun_device_debug_print_video_stats.argtypes = [ctypes.POINTER(hdhomerun_device_t)]
    hdhomerun_device_debug_print_video_stats.restype = None
if hasattr(__libs['hdhomerun'], 'hdhomerun_device_get_video_stats'):
    hdhomerun_device_get_video_stats = __libs['hdhomerun'].hdhomerun_device_get_video_stats
    hdhomerun_device_get_video_stats.argtypes = [ctypes.POINTER(hdhomerun_device_t), ctypes.POINTER(hdhomerun_video_stats_t)]
    hdhomerun_device_get_video_stats.restype = None
if hasattr(__libs['hdhomerun'], 'hdhomerun_discover_find_devices_custom'):
    hdhomerun_discover_find_devices_custom = __libs['hdhomerun'].hdhomerun_discover_find_devices_custom
    hdhomerun_discover_find_devices_custom.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(hdhomerun_discover_device_t), ctypes.c_int]
    hdhomerun_discover_find_devices_custom.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_discover_create'):
    hdhomerun_discover_create = __libs['hdhomerun'].hdhomerun_discover_create
    hdhomerun_discover_create.argtypes = None
    hdhomerun_discover_create.restype = hdhomerun_discover_device_t
if hasattr(__libs['hdhomerun'], 'hdhomerun_discover_destroy'):
    hdhomerun_discover_destroy = __libs['hdhomerun'].hdhomerun_discover_destroy
    hdhomerun_discover_destroy.argtypes = [ctypes.POINTER(hdhomerun_discover_device_t)]
    hdhomerun_discover_destroy.restype = None
if hasattr(__libs['hdhomerun'], 'hdhomerun_discover_find_devices'):
    hdhomerun_discover_find_devices = __libs['hdhomerun'].hdhomerun_discover_find_devices
    hdhomerun_discover_find_devices.argtypes = [ctypes.POINTER(hdhomerun_discover_device_t), ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(hdhomerun_discover_device_t), ctypes.c_int]
    hdhomerun_discover_find_devices.restype = ctypes.c_int
if hasattr(__libs['hdhomerun'], 'hdhomerun_discover_validate_device_id'):
    hdhomerun_discover_validate_device_id = __libs['hdhomerun'].hdhomerun_discover_validate_device_id
    hdhomerun_discover_validate_device_id.argtypes = [ctypes.c_uint32]
    hdhomerun_discover_validate_device_id.restype = ctypes.c_int32
if hasattr(__libs['hdhomerun'], 'hdhomerun_discover_is_ip_multicast'):
    hdhomerun_discover_is_ip_multicast = __libs['hdhomerun'].hdhomerun_discover_is_ip_multicast
    hdhomerun_discover_is_ip_multicast.argtypes = [ctypes.c_uint32]
    hdhomerun_discover_is_ip_multicast.restype = ctypes.c_int32
if hasattr(__libs['hdhomerun'], 'hdhomerun_channelmap_get_channelmap_scan_group'):
    hdhomerun_channelmap_get_channelmap_scan_group = __libs['hdhomerun'].hdhomerun_channelmap_get_channelmap_scan_group
    hdhomerun_channelmap_get_channelmap_scan_group.argtypes = [ctypes.c_char_p]
    hdhomerun_channelmap_get_channelmap_scan_group.restype = ctypes.c_char_p

