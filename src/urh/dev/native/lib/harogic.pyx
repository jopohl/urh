cimport numpy as np
import numpy as np
cimport urh.dev.native.lib.charogic as charogic
from libc.stdint cimport uint32_t
from urh.util.Logger import logger

np.import_array()

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
    devices = []
    for i in range(128):
        if charogic.Device_Open(&dev_tmp, i, &profile, &binfo) < 0:
            break
        label = "Harogic " + "{:X}".format(binfo.DeviceInfo.DeviceUID)
        devices.append(label)
        charogic.Device_Close(&dev_tmp)
    return devices

cpdef int open_device(str identifier):
    global _is_open, _c_device
    if _is_open: return 0

    cdef int target_index = 0
    cdef bint found = False
    cdef charogic.BootProfile_TypeDef profile
    cdef charogic.BootInfo_TypeDef binfo
    cdef void* dev_tmp
    cdef str label

    if identifier:
        profile.PhysicalInterface = charogic.USB
        profile.DevicePowerSupply = charogic.USBPortOnly
        for i in range(128):
            if charogic.Device_Open(&dev_tmp, i, &profile, &binfo) < 0: break
            label = "Harogic " + "{:X}".format(binfo.DeviceInfo.DeviceUID)
            charogic.Device_Close(&dev_tmp)
            if label == identifier:
                target_index = i
                found = True
                break
        if not found:
            logger.warning(f"Harogic: Device '{identifier}' not found, falling back to index 0.")

    profile.DevicePowerSupply = charogic.USBPortAndPowerPort
    ret = charogic.Device_Open(&_c_device, target_index, &profile, &binfo)
    if ret == 0:
        _is_open = True
        logger.info(f"Harogic device index {target_index} opened successfully.")
        charogic.IQS_ProfileDeInit(&_c_device, &_profile)
    else:
        logger.error(f"Harogic: Failed to open device index {target_index} with error code {ret}.")
    return ret

cpdef int configure_and_start_rx(double freq, double sample_rate, double gain, int format_index, double if_gain, double baseband_gain):
    global _profile, _stream_info
    
    _profile.CenterFreq_Hz = freq
    _profile.RefLevel_dBm = gain
    _profile.DecimateFactor = <uint32_t>(122.88e6 / sample_rate)
    _profile.BusTimeout_ms = 100
    _profile.TriggerSource = charogic.Bus
    _profile.TriggerMode = charogic.Adaptive
    _profile.Atten = -1
    
    if format_index == 2: _profile.DataFormat = charogic.Complex32bit
    elif format_index == 0: _profile.DataFormat = charogic.Complex8bit
    else: _profile.DataFormat = charogic.Complex16bit

    _profile.EnableIFAGC = 1 if if_gain > 0 else 0
    _profile.Preamplifier = charogic.AutoOn if baseband_gain > 0 else charogic.ForcedOff

    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0:
        logger.error(f"Harogic: IQS_Configuration failed with error {ret}.")
        return ret
    return charogic.IQS_BusTriggerStart(&_c_device)

cpdef get_samples():
    global _iq_stream

    # Corrected syntax: declarations on separate lines
    cdef np.ndarray[np.complex64_t, ndim=1] final_complex
    cdef np.ndarray[np.float32_t, ndim=1] interleaved_float_out
    
    ret = charogic.IQS_GetIQStream_PM1(&_c_device, &_iq_stream)
    if ret < 0: return 0, b''

    cdef int num_samples = _iq_stream.IQS_StreamInfo.PacketSamples
    cdef float scale_factor = _iq_stream.IQS_ScaleToV
    if num_samples == 0: return 0, b''

    if _profile.DataFormat == charogic.Complexfloat:
        raw_data_view = <np.complex64_t[:num_samples]>_iq_stream.AlternIQStream
        final_complex = np.asarray(raw_data_view)
    elif _profile.DataFormat == charogic.Complex32bit:
        raw_data_view = <np.int32_t[:num_samples*2]>_iq_stream.AlternIQStream
        raw_data_np = np.asarray(raw_data_view)
        interleaved_float = raw_data_np.astype(np.float32)
        final_complex = (interleaved_float[0::2] + 1j * interleaved_float[1::2]) * scale_factor
    elif _profile.DataFormat == charogic.Complex8bit:
        raw_data_view = <np.int8_t[:num_samples*2]>_iq_stream.AlternIQStream
        raw_data_np = np.asarray(raw_data_view)
        interleaved_float = raw_data_np.astype(np.float32)
        final_complex = (interleaved_float[0::2] + 1j * interleaved_float[1::2]) * scale_factor
    else: # Complex16bit
        raw_data_view = <np.int16_t[:num_samples*2]>_iq_stream.AlternIQStream
        raw_data_np = np.asarray(raw_data_view)
        interleaved_float = raw_data_np.astype(np.float32)
        final_complex = (interleaved_float[0::2] + 1j * interleaved_float[1::2]) * scale_factor

    interleaved_float_out = np.empty(num_samples * 2, dtype=np.float32)
    interleaved_float_out[0::2] = np.real(final_complex)
    interleaved_float_out[1::2] = np.imag(final_complex)

    return num_samples, interleaved_float_out.tobytes()

cpdef int close_device():
    global _is_open
    if not _is_open: return 0
    ret = charogic.Device_Close(&_c_device)
    if ret == 0: _is_open = False
    return ret
    
cpdef stop_rx():
    return charogic.IQS_BusTriggerStop(&_c_device)

cpdef int set_if_agc(double value):
    if not _is_open: return -1
    charogic.IQS_BusTriggerStop(&_c_device)
    _profile.EnableIFAGC = 1 if value > 0 else 0
    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0: return ret
    return charogic.IQS_BusTriggerStart(&_c_device)

cpdef int set_preamp(double value):
    if not _is_open: return -1
    charogic.IQS_BusTriggerStop(&_c_device)
    _profile.Preamplifier = charogic.AutoOn if value > 0 else charogic.ForcedOff
    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0: return ret
    return charogic.IQS_BusTriggerStart(&_c_device)

cpdef int set_data_format(int index):
    if not _is_open: return -1
    charogic.IQS_BusTriggerStop(&_c_device)
    if index == 2: _profile.DataFormat = charogic.Complex32bit
    elif index == 0: _profile.DataFormat = charogic.Complex8bit
    else: _profile.DataFormat = charogic.Complex16bit
    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0: return ret
    return charogic.IQS_BusTriggerStart(&_c_device)

cpdef int set_frequency(double new_freq):
    if not _is_open: return -1
    charogic.IQS_BusTriggerStop(&_c_device)
    _profile.CenterFreq_Hz = new_freq
    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0: return ret
    return charogic.IQS_BusTriggerStart(&_c_device)

cpdef int set_ref_level(double new_gain):
    if not _is_open: return -1
    charogic.IQS_BusTriggerStop(&_c_device)
    _profile.RefLevel_dBm = new_gain
    ret = charogic.IQS_Configuration(&_c_device, &_profile, &_profile, &_stream_info)
    if ret != 0: return ret
    return charogic.IQS_BusTriggerStart(&_c_device)

def get_data_type():
    if _profile.DataFormat == charogic.Complex32bit: return 'int32'
    elif _profile.DataFormat == charogic.Complex8bit: return 'int8'
    else: return 'int16'
