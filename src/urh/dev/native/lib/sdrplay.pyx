cimport csdrplay
from libc.stdlib cimport malloc, free

ctypedef csdrplay.mir_sdr_DeviceT device_type
ctypedef csdrplay.mir_sdr_ErrT error_t

cdef extern from "Python.h":
    ctypedef int PyGILState_STATE
    PyGILState_STATE PyGILState_Ensure()
    void PyGILState_Release(PyGILState_STATE)

cdef void _rx_stream_callback(short *xi, short *xq, unsigned int firstSampleNum, int grChanged, int rfChanged, int fsChanged, unsigned int numSamples, unsigned int reset, void *cbContext):
    cdef short* data = <short *>malloc(2*numSamples * sizeof(short))

    cdef unsigned int i = 0
    cdef unsigned int j = 0

    cdef PyGILState_STATE gstate
    try:
        for i in range(0, numSamples):
            data[j] = xi[i]
            data[j+1] = xq[i]
            j += 2

        gstate = PyGILState_Ensure()
        func = <object> cbContext
        func(<short[:2*numSamples]>data)  # python callback
        return
    finally:
        PyGILState_Release(gstate)
        free(data)

cdef void _gain_change_callback(unsigned int gRdB, unsigned int lnaGRdB, void *cbContext):
    return

cpdef float get_api_version():
    cdef float version = 0.0
    csdrplay.mir_sdr_ApiVersion(&version)
    return version

cpdef get_devices():
    cdef device_type *devs = <device_type*> malloc(256 * sizeof(device_type))

    if not devs:
        raise MemoryError()

    cdef unsigned int num_devs = 0
    try:
        csdrplay.mir_sdr_GetDevices(devs, &num_devs, 256)

        result = []

        for i in range(num_devs):
            d = {"serial": devs[i].SerNo.decode("utf-8"), "device_ref": devs[i].DevNm.decode("utf-8"),
                 "hw_version": devs[i].hwVer, "available": devs[i].devAvail}
            result.append(d)

        return result
    finally:
        free(devs)

cpdef init_stream(int gain, double sample_rate, double center_freq, double bandwidth, double if_gain, object func):
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

    # get nearest ifgain
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

    lna_state = 0  # todo
    cdef int gRdBsystem = 0
    cdef csdrplay.mir_sdr_SetGrModeT gr_mode = csdrplay.mir_sdr_USE_RSP_SET_GR
    cdef int samples_per_packet = 0

    return csdrplay.mir_sdr_StreamInit(&gain, sample_rate / 1e6, center_freq / 1e6, bw_type, if_type, lna_state,
                                       &gRdBsystem, gr_mode, &samples_per_packet, _rx_stream_callback,
                                       _gain_change_callback, <void *> func)
