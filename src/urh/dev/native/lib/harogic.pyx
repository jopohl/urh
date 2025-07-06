cimport urh.dev.native.lib.charogic as charogic
from libc.stdlib cimport malloc, free
from libc.stdint cimport uint32_t
from cython.view cimport array as cvarray
from urh.util.Logger import logger

cdef void* _c_device
cdef charogic.IQS_Profile_TypeDef _profile
cdef charogic.IQS_StreamInfo_TypeDef _stream_info
cdef charogic.IQStream_TypeDef _iq_stream
cdef bint _is_open = False

cpdef list get_device_list():
    cdef charogic.BootProfile_TypeDef profile
    profile.PhysicalInterface = charogic.USB
    profile.DevicePowerSupply = charogic.USBPortOnly
    
    cdef void* dev_tmp
    cdef charogic.BootInfo_TypeDef binfo
    cdef int i = 0
    
    devices = []
    
    for i in range(128):
        if charogic.Device_Open(&dev_tmp, i, &profile, &binfo) < 0:
            break
        
        serial_str = "{:X}".format(binfo.DeviceInfo.DeviceUID)
        label = "Harogic " + serial_str
        devices.append((label, serial_str))
        charogic.Device_Close(&dev_tmp)
        
    return devices
    
cpdef int open_device(int device_index):
    global _is_open
    if _is_open:
        return 0

    cdef charogic.BootProfile_TypeDef profile
    profile.PhysicalInterface = charogic.USB
    profile.DevicePowerSupply = charogic.USBPortAndPowerPort # Use more power for streaming
    
    cdef charogic.BootInfo_TypeDef binfo
    
    ret = charogic.Device_Open(&_c_device, device_index, &profile, &binfo)
    if ret == 0:
        _is_open = True
        logger.info("Harogic device opened successfully.")
        # Prepare a default profile
        charogic.IQS_ProfileDeInit(&_c_device, &_profile)
    return ret

cpdef int close_device():
    global _is_open
    if not _is_open:
        return 0
    ret = charogic.Device_Close(&_c_device)
    if ret == 0:
        _is_open = False
    return ret

cpdef int configure_and_start_rx(double freq, double sample_rate, double gain):
    global _profile, _stream_info
    
    _profile.CenterFreq_Hz = freq
    _profile.RefLevel_dBm = gain
    _profile.DecimateFactor = <uint32_t>(122.88e6 / sample_rate) # Assuming 122.88M is a base rate
    _profile.BusTimeout_ms = 1000
    _profile.TriggerSource = charogic.Bus
    _profile.TriggerMode = charogic.Adaptive
    _profile.Atten = -1 # Auto-attenuation
    
    # Use 8-bit samples for high sample rates, 16-bit for lower
    if sample_rate > 62e6:
        _profile.DataFormat = charogic.Complex8bit
    else:
        _profile.DataFormat = charogic.Complex16bit

    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0:
        logger.error(f"Harogic IQS_Configuration failed: {ret}")
        return ret
    
    ret = charogic.IQS_BusTriggerStart(&_c_device)
    if ret != 0:
        logger.error(f"Harogic IQS_BusTriggerStart failed: {ret}")

    return ret

cpdef stop_rx():
    return charogic.IQS_BusTriggerStop(&_c_device)

cpdef int set_frequency(double new_freq):
    global _profile, _stream_info
    if not _is_open:
        return -1 # Or some other error code

    _profile.CenterFreq_Hz = new_freq
    
    # Re-configure the device with the updated profile
    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0:
        logger.error(f"Harogic set_frequency->IQS_Configuration failed: {ret}")
        return ret

    ret = charogic.IQS_BusTriggerStart(&_c_device)
    if ret != 0:
        logger.error(f"Harogic set_frequency->IQS_BusTriggerStart failed: {ret}")


    return ret

cpdef int set_ref_level(double new_gain):
    global _profile, _stream_info
    if not _is_open:
        return -1

    _profile.RefLevel_dBm = new_gain
    
    # Re-configure the device with the updated profile
    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0:
        logger.error(f"Harogic set_ref_level->IQS_Configuration failed: {ret}")

    return ret

cpdef get_samples():
    global _iq_stream
    ret = charogic.IQS_GetIQStream_PM1(&_c_device, &_iq_stream)
    
    if ret < 0:
        # Don't return error on timeout, just empty data
        if ret == -10: # APIRETVAL_WARNING_BusTimeOut
            return 0, b''
        return ret, b''

    cdef int num_samples = _iq_stream.IQS_StreamInfo.PacketSamples
    cdef int bytes_per_sample
    
    if _profile.DataFormat == charogic.Complex8bit:
        bytes_per_sample = 2 # 1 byte for I, 1 for Q
    else: # Complex16bit
        bytes_per_sample = 4 # 2 bytes for I, 2 for Q
    
    cdef int total_bytes = num_samples * bytes_per_sample
    
    # Create a Python bytes object by copying the data from the C buffer
    py_bytes = (<char*>_iq_stream.AlternIQStream)[:total_bytes]
    
    return num_samples, py_bytes

def get_data_type():
    if _profile.DataFormat == charogic.Complex8bit:
        return 'int8'
    else:
        return 'int16'