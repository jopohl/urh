cimport urh.dev.native.lib.csdrplay as csdrplay
import time
from libc.stdlib cimport malloc, free

ctypedef csdrplay.mir_sdr_DeviceT device_type
ctypedef csdrplay.mir_sdr_ErrT error_t

cdef extern from "Python.h":
    ctypedef enum PyGILState_STATE:
        PyGILState_LOCKED
        PyGILState_UNLOCKED
    PyGILState_STATE PyGILState_Ensure()
    void PyGILState_Release(PyGILState_STATE)



cdef csdrplay.mir_sdr_SetGrModeT set_gr_mode=csdrplay.mir_sdr_USE_RSP_SET_GR

global reset_rx, reset_rx_request_received
reset_rx = False
reset_rx_request_received = False

cdef void __rx_stream_callback(short *xi, short *xq, unsigned int firstSampleNum, int grChanged, int rfChanged, int fsChanged, unsigned int numSamples, unsigned int reset, void *cbContext):
    cdef short* data = <short *>malloc(2*numSamples * sizeof(short))

    cdef unsigned int i = 0
    cdef unsigned int j = 0

    global reset_rx, reset_rx_request_received
    if reset_rx:
        reset_rx_request_received = True
        return

    cdef PyGILState_STATE gstate

    try:
        for i in range(0, numSamples):
            data[j] = xi[i]
            data[j+1] = xq[i]
            j += 2

        gstate = PyGILState_Ensure()
        conn = <object> cbContext
        conn.send_bytes(<short[:2*numSamples]>data)  # python callback
        return
    finally:
        PyGILState_Release(gstate)
        free(data)

cdef void _rx_stream_callback(short *xi, short *xq, unsigned int firstSampleNum, int grChanged, int rfChanged, int fsChanged, unsigned int numSamples, unsigned int reset, unsigned int hwRemoved, void *cbContext) noexcept:
    __rx_stream_callback(xi, xq, firstSampleNum, grChanged, rfChanged, fsChanged, numSamples, reset, cbContext)

cdef void _gain_change_callback(unsigned int gRdB, unsigned int lnaGRdB, void *cbContext) noexcept:
    return

cpdef void set_gr_mode_for_dev_model(int dev_model):
    global set_gr_mode
    if dev_model == 1:
        set_gr_mode = csdrplay.mir_sdr_USE_SET_GR_ALT_MODE
    else:
        set_gr_mode = csdrplay.mir_sdr_USE_RSP_SET_GR

cpdef float get_api_version():
    cdef float version = 0.0
    csdrplay.mir_sdr_ApiVersion(&version)
    return version

cpdef error_t set_device_index(unsigned int index):
    return csdrplay.mir_sdr_SetDeviceIdx(index)

cpdef error_t release_device_index():
    return csdrplay.mir_sdr_ReleaseDeviceIdx()

cpdef get_devices():
    cdef device_type *devs = <device_type*> malloc(256 * sizeof(device_type))

    if not devs:
        raise MemoryError()

    cdef unsigned int num_devs = 0
    try:
        csdrplay.mir_sdr_GetDevices(devs, &num_devs, 256)

        result = []

        for i in range(num_devs):
            d = {"serial": devs[i].SerNo.decode("iso-8859-1"), "device_ref": devs[i].DevNm.decode("iso-8859-1"),
                 "hw_version": devs[i].hwVer, "available": devs[i].devAvail}
            result.append(d)

        return result
    finally:
        free(devs)

cdef int calculate_gain_reduction(int gain):
    """
    Calculate gain reduction for API. Highest possible gain leads to lowest possible gain reduction
    :param gain:
    :return:
    """
    gain = max(20, min(gain, 59))
    return 79 - gain

cdef csdrplay.mir_sdr_Bw_MHzT get_nearest_bandwidth(double bandwidth):
    # get nearest bwtype
    bandwidths = {200e3: csdrplay.mir_sdr_BW_0_200,
                  300e3: csdrplay.mir_sdr_BW_0_300,
                  600e3: csdrplay.mir_sdr_BW_0_600,
                  1536e3: csdrplay.mir_sdr_BW_1_536,
                  5000e3: csdrplay.mir_sdr_BW_5_000,
                  6000e3: csdrplay.mir_sdr_BW_6_000,
                  7000e3: csdrplay.mir_sdr_BW_7_000,
                  8000e3: csdrplay.mir_sdr_BW_8_000}

    cdef csdrplay.mir_sdr_Bw_MHzT bw_type = csdrplay.mir_sdr_Bw_MHzT.mir_sdr_BW_0_200
    best_match = 0
    for bw in bandwidths:
        if abs(bw - bandwidth) < abs(best_match - bandwidth):
            best_match = bw
    bw_type = bandwidths[best_match]
    return bw_type

cdef csdrplay.mir_sdr_If_kHzT get_nearest_if_gain(double if_gain):
    cdef csdrplay.mir_sdr_If_kHzT if_type = csdrplay.mir_sdr_If_kHzT.mir_sdr_IF_Zero
    best_match = 0
    if_types = {0: csdrplay.mir_sdr_IF_Zero,
                450: csdrplay.mir_sdr_IF_0_450,
                1620: csdrplay.mir_sdr_IF_1_620,
                2048: csdrplay.mir_sdr_IF_2_048}
    for i in if_types:
        if abs(i - if_gain) < abs(best_match - if_gain):
            best_match = i

    if_type = if_types[best_match]
    return if_type

cpdef init_stream(int gain, double sample_rate, double center_freq, double bandwidth, double if_gain, object func):
    global set_gr_mode

    cdef csdrplay.mir_sdr_Bw_MHzT bw_type = get_nearest_bandwidth(bandwidth)
    # get nearest ifgain
    cdef csdrplay.mir_sdr_If_kHzT if_type = get_nearest_if_gain(if_gain)

    lna_state = 0
    cdef int gRdBsystem = 0
    cdef int samples_per_packet = 0

    cdef int gain_reduction = calculate_gain_reduction(gain)
    return csdrplay.mir_sdr_StreamInit(&gain_reduction, sample_rate / 1e6, center_freq / 1e6, bw_type, if_type, lna_state,
                                       &gRdBsystem, set_gr_mode, &samples_per_packet, _rx_stream_callback,
                                       _gain_change_callback, <void *> func)

cpdef error_t set_center_freq(double frequency):
    return reinit_stream(csdrplay.mir_sdr_CHANGE_RF_FREQ, frequency=frequency)

cpdef error_t set_sample_rate(double sample_rate):
    return reinit_stream(csdrplay.mir_sdr_CHANGE_FS_FREQ, sample_rate=sample_rate)

cpdef error_t set_bandwidth(double bandwidth):
    cdef csdrplay.mir_sdr_Bw_MHzT bw_type = get_nearest_bandwidth(bandwidth)
    return reinit_stream(csdrplay.mir_sdr_CHANGE_BW_TYPE, bw_type=bw_type)

cpdef error_t set_gain(int gain):
    return reinit_stream(csdrplay.mir_sdr_CHANGE_GR, gain=calculate_gain_reduction(gain))

cpdef error_t set_if_gain(double if_gain):
    cdef csdrplay.mir_sdr_If_kHzT if_type = get_nearest_if_gain(if_gain)
    return reinit_stream(csdrplay.mir_sdr_CHANGE_IF_TYPE, if_type=if_type)

cpdef error_t set_antenna(int antenna):
    cdef csdrplay.mir_sdr_RSPII_AntennaSelectT antenna_select
    if antenna == 0 or antenna == 1:
        result = csdrplay.mir_sdr_AmPortSelect(0)
        if result != csdrplay.mir_sdr_Success:
            return result

        if antenna == 0:
            antenna_select = csdrplay.mir_sdr_RSPII_ANTENNA_A
        else:
            antenna_select = csdrplay.mir_sdr_RSPII_ANTENNA_B

        return csdrplay.mir_sdr_RSPII_AntennaControl(antenna_select)
    elif antenna == 2:
        print("hiz")
        return csdrplay.mir_sdr_AmPortSelect(1)


cpdef error_t reinit_stream(csdrplay.mir_sdr_ReasonForReinitT reason_for_reinit,
                            double sample_rate=0, double frequency=0,
                            csdrplay.mir_sdr_Bw_MHzT bw_type=csdrplay.mir_sdr_BW_Undefined,
                            int gain=0,
                            csdrplay.mir_sdr_If_kHzT if_type=csdrplay.mir_sdr_IF_Undefined,
                            csdrplay.mir_sdr_LoModeT lo_mode=csdrplay.mir_sdr_LO_Undefined,
                            int lna_state=0):
    cdef int gRdBsystem, samplesPerPacket
    global reset_rx, reset_rx_request_received, set_gr_mode
    reset_rx = True

    while not reset_rx_request_received:
        time.sleep(0.01)

    try:
        return csdrplay.mir_sdr_Reinit(&gain, sample_rate / 1e6, frequency / 1e6, bw_type, if_type, lo_mode, lna_state, &gRdBsystem, set_gr_mode, &samplesPerPacket, reason_for_reinit)
    finally:
        reset_rx = False
        reset_rx_request_received = False

cpdef error_t close_stream():
    csdrplay.mir_sdr_StreamUninit()
