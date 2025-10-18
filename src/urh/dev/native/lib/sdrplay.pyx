cimport urh.dev.native.lib.csdrplay as csdrplay
import time
from libc.stdlib cimport malloc, free
from libcpp cimport bool

ctypedef csdrplay.sdrplay_api_DeviceT device_type
ctypedef csdrplay.sdrplay_api_ErrT error_t

cdef device_type g_device
cdef csdrplay.sdrplay_api_DeviceParamsT* g_devParams = NULL
cdef csdrplay.sdrplay_api_TunerSelectT g_tuner = csdrplay.sdrplay_api_Tuner_A
cdef bool reset_rx = False

cdef void __rx_stream_callback(short *xi, short *xq, csdrplay.sdrplay_api_StreamCbParamsT *params, unsigned int numSamples, unsigned int reset, void *cbContext) noexcept nogil:
    global reset_rx
    if reset_rx:
        return

    cdef short* data = <short *>malloc(2*numSamples * sizeof(short))
    if data == NULL:
        return
    cdef unsigned int i = 0
    cdef unsigned int j = 0
    for i in range(0, numSamples):
        data[j] = xi[i]
        data[j+1] = xq[i]
        j += 2

    try:
        with gil:
            (<object> cbContext).send_bytes(<short[:2*numSamples]>data)  # python callback
    finally:
        free(data)

cdef void _stream_a_callback(short *xi, short *xq,
                             csdrplay.sdrplay_api_StreamCbParamsT *params,
                             unsigned int numSamples,
                             unsigned int reset,
                             void *cbContext) noexcept nogil:
    __rx_stream_callback(xi, xq, params,
                         numSamples, reset, cbContext)

cdef void _stream_b_callback(short* xi, short* xq,
                             csdrplay.sdrplay_api_StreamCbParamsT* params,
                             unsigned int numSamples,
                             unsigned int reset,
                             void* cbContext) noexcept nogil:
    pass

cdef void _event_callback(csdrplay.sdrplay_api_EventT eventId,
                          csdrplay.sdrplay_api_TunerSelectT tuner,
                          csdrplay.sdrplay_api_EventParamsT* params,
                          void* cbContext) noexcept nogil:
    pass

# Keep the old interface name, internally do the v3 equivalent (set minimum gain range)
cpdef error_t set_gr_mode_for_dev_model(int dev_model):
    # Requires global g_device / g_devParams / g_tuner (which we have already established)
    if g_device.dev == NULL or g_devParams == NULL:
        return csdrplay.sdrplay_api_NotInitialised

    # Convention: dev_model == 1 means RSP1
    if dev_model == 1:
        g_devParams.rxChannelA.tunerParams.gain.minGr = csdrplay.sdrplay_api_EXTENDED_MIN_GR
    else:
        g_devParams.rxChannelA.tunerParams.gain.minGr = csdrplay.sdrplay_api_NORMAL_MIN_GR

    return csdrplay.sdrplay_api_Update(
        g_device.dev,
        g_tuner,
        <csdrplay.sdrplay_api_ReasonForUpdateT> csdrplay.sdrplay_api_Update_Tuner_GrLimits,
        csdrplay.sdrplay_api_Update_Ext1_None
    )

cpdef float get_api_version() noexcept nogil:
    cdef float version = 0.0
    csdrplay.sdrplay_api_ApiVersion(&version)
    return version

cpdef error_t open_api() noexcept nogil:
    """
    Explicitly open the SDRPlay API session.
    Should be called before any device operations.
    """
    return csdrplay.sdrplay_api_Open()

cpdef error_t close_api() noexcept nogil:
    """
    Explicitly close the SDRPlay API session.
    Should be called after all device operations are complete.
    """
    return csdrplay.sdrplay_api_Close()

cpdef error_t set_device_index(unsigned int index):
    """
    Select and lock a device by index.
    Requires open_api() to be called first.
    """
    global g_device, g_devParams
    cdef device_type* devs = <device_type*> malloc(16 * sizeof(device_type))
    cdef error_t err

    if not devs:
        raise MemoryError()

    cdef unsigned int num_devs = 0
    try:
        err = csdrplay.sdrplay_api_GetDevices(devs, &num_devs, 16)
        if err != csdrplay.sdrplay_api_Success:
            return err
        if index >= num_devs:
            return csdrplay.sdrplay_api_OutOfRange

        # Select the target device
        g_device = devs[index]
        err = csdrplay.sdrplay_api_SelectDevice(&g_device)
        if err != csdrplay.sdrplay_api_Success:
            return err

        # Save the handle and get the parameter tree
        err = csdrplay.sdrplay_api_GetDeviceParams(g_device.dev, &g_devParams)
        if err != csdrplay.sdrplay_api_Success:
            # If it fails, release the device to avoid occupying it
            csdrplay.sdrplay_api_ReleaseDevice(&g_device)
            g_devParams = NULL
            return err

        return csdrplay.sdrplay_api_Success
    finally:
        free(devs)

cpdef error_t release_device_index() noexcept nogil:
    return csdrplay.sdrplay_api_ReleaseDevice(&g_device)

cpdef get_devices():
    cdef device_type *devs = <device_type*> malloc(16 * sizeof(device_type))
    cdef error_t err

    if not devs:
        raise MemoryError()

    cdef unsigned int num_devs = 0
    try:
        err = csdrplay.sdrplay_api_GetDevices(devs, &num_devs, 16)
        if err != csdrplay.sdrplay_api_Success:
            raise RuntimeError(f"Failed to get devices: {err}")

        result = []

        for i in range(num_devs):
            d = {"serial": devs[i].SerNo.decode("iso-8859-1"),
                 "hw_version": devs[i].hwVer}
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

cdef csdrplay.sdrplay_api_Bw_MHzT get_nearest_bandwidth(double bandwidth):
    # get nearest bwtype
    bandwidths = {200e3: csdrplay.sdrplay_api_BW_0_200,
                  300e3: csdrplay.sdrplay_api_BW_0_300,
                  600e3: csdrplay.sdrplay_api_BW_0_600,
                  1536e3: csdrplay.sdrplay_api_BW_1_536,
                  5000e3: csdrplay.sdrplay_api_BW_5_000,
                  6000e3: csdrplay.sdrplay_api_BW_6_000,
                  7000e3: csdrplay.sdrplay_api_BW_7_000,
                  8000e3: csdrplay.sdrplay_api_BW_8_000}

    cdef csdrplay.sdrplay_api_Bw_MHzT bw_type = csdrplay.sdrplay_api_Bw_MHzT.sdrplay_api_BW_0_200
    best_match = 0
    for bw in bandwidths:
        if abs(bw - bandwidth) < abs(best_match - bandwidth):
            best_match = bw
    bw_type = bandwidths[best_match]
    return bw_type

cdef csdrplay.sdrplay_api_If_kHzT get_nearest_if_gain(double if_gain):
    cdef csdrplay.sdrplay_api_If_kHzT if_type = csdrplay.sdrplay_api_If_kHzT.sdrplay_api_IF_Zero
    best_match = 0
    if_types = {0: csdrplay.sdrplay_api_IF_Zero,
                450: csdrplay.sdrplay_api_IF_0_450,
                1620: csdrplay.sdrplay_api_IF_1_620,
                2048: csdrplay.sdrplay_api_IF_2_048}
    for i in if_types:
        if abs(i - if_gain) < abs(best_match - if_gain):
            best_match = i

    if_type = if_types[best_match]
    return if_type

# According to SDRPlay API v3 docs:
# Conditions for LIF down-conversion to be enabled for RSP1, RSP1a, RSP2a and RSPduo in single tuner mode:
# (fsHz == 8192000) && (bwType == sdrplay_api_BW_1_536) && (ifType == sdrplay_api_IF_2_048)
# (fsHz == 8000000) && (bwType == sdrplay_api_BW_1_536) && (ifType == sdrplay_api_IF_2_048)
# (fsHz == 8000000) && (bwType == sdrplay_api_BW_5_000) && (ifType == sdrplay_api_IF_2_048)
# (fsHz == 2000000) && (bwType <= sdrplay_api_BW_0_300) && (ifType == sdrplay_api_IF_0_450)
# (fsHz == 2000000) && (bwType == sdrplay_api_BW_0_600) && (ifType == sdrplay_api_IF_0_450)
# (fsHz == 6000000) && (bwType <= sdrplay_api_BW_1_536) && (ifType == sdrplay_api_IF_1_620)
cpdef error_t init_stream(int gain, double sample_rate, double center_freq, double bandwidth, double if_gain, object func):
    if g_device.dev == NULL or g_devParams == NULL:
        return csdrplay.sdrplay_api_NotInitialised

    # Calculate the nearest BW / IF
    cdef csdrplay.sdrplay_api_Bw_MHzT bw_type = get_nearest_bandwidth(bandwidth)
    cdef csdrplay.sdrplay_api_If_kHzT if_type = get_nearest_if_gain(if_gain)

    # Write initial parameters into the parameter tree (v3 unit is Hz, not MHz)
    g_devParams.devParams.fsFreq.fsHz              = sample_rate
    g_devParams.rxChannelA.tunerParams.rfFreq.rfHz = center_freq
    g_devParams.rxChannelA.tunerParams.bwType      = bw_type
    g_devParams.rxChannelA.tunerParams.ifType      = if_type
    g_devParams.rxChannelA.tunerParams.loMode      = csdrplay.sdrplay_api_LO_Auto  # Common default

    # Gain: map UI "gain" to gRdB (IF attenuation, the larger the value, the smaller the gain)
    cdef int gRdB = calculate_gain_reduction(gain)
    g_devParams.rxChannelA.tunerParams.gain.gRdB     = gRdB
    g_devParams.rxChannelA.tunerParams.gain.LNAstate = 0
    g_devParams.rxChannelA.tunerParams.gain.minGr    = csdrplay.sdrplay_api_NORMAL_MIN_GR

    # Assemble the callback structure
    cdef csdrplay.sdrplay_api_CallbackFnsT cbs
    cbs.StreamACbFn = _stream_a_callback
    cbs.StreamBCbFn = _stream_b_callback
    cbs.EventCbFn   = _event_callback

    # Init: start the stream processing thread according to the current parameter tree
    return csdrplay.sdrplay_api_Init(g_device.dev, &cbs, <void*> func)

cpdef error_t set_center_freq(double frequency):
    return update_params(csdrplay.sdrplay_api_Update_Tuner_Frf, frequency=frequency)

cpdef error_t set_sample_rate(double sample_rate):
    return update_params(csdrplay.sdrplay_api_Update_Dev_Fs, sample_rate=sample_rate)

cpdef error_t set_bandwidth(double bandwidth):
    cdef csdrplay.sdrplay_api_Bw_MHzT bw_type = get_nearest_bandwidth(bandwidth)
    return update_params(csdrplay.sdrplay_api_Update_Tuner_BwType, bw_type=bw_type)

cpdef error_t set_gain(int gain_ui):
    cdef int gRdB = calculate_gain_reduction(gain_ui)
    return update_params(csdrplay.sdrplay_api_Update_Tuner_Gr, gain=gRdB)

cpdef error_t set_if_gain(double if_gain):
    cdef csdrplay.sdrplay_api_If_kHzT if_type = get_nearest_if_gain(if_gain)
    return update_params(csdrplay.sdrplay_api_Update_Tuner_IfType, if_type=if_type)

cpdef error_t set_antenna(int antenna):
    if g_device.dev == NULL or g_devParams == NULL:
        return csdrplay.sdrplay_api_NotInitialised

    cdef unsigned int reason = 0

    if antenna == 0 or antenna == 1:
        # Use 50Ω A/B ports: first switch back to AMPORT_2, then select A or B
        g_devParams.rxChannelA.rsp2TunerParams.amPortSel = csdrplay.sdrplay_api_Rsp2_AMPORT_2
        reason |= csdrplay.sdrplay_api_Update_Rsp2_AmPortSelect

        if antenna == 0:
            g_devParams.rxChannelA.rsp2TunerParams.antennaSel = csdrplay.sdrplay_api_Rsp2_ANTENNA_A
        else:
            g_devParams.rxChannelA.rsp2TunerParams.antennaSel = csdrplay.sdrplay_api_Rsp2_ANTENNA_B
        reason |= csdrplay.sdrplay_api_Update_Rsp2_AntennaControl

    elif antenna == 2:
        # Hi-Z port
        g_devParams.rxChannelA.rsp2TunerParams.amPortSel = csdrplay.sdrplay_api_Rsp2_AMPORT_1
        reason |= csdrplay.sdrplay_api_Update_Rsp2_AmPortSelect
    else:
        return csdrplay.sdrplay_api_OutOfRange

    return csdrplay.sdrplay_api_Update(
        g_device.dev, g_tuner, <csdrplay.sdrplay_api_ReasonForUpdateT>reason, csdrplay.sdrplay_api_Update_Ext1_None
    )

cpdef error_t update_params(
    unsigned int reason_flags,
    double sample_rate=0,
    double frequency=0,
    csdrplay.sdrplay_api_Bw_MHzT bw_type=csdrplay.sdrplay_api_BW_Undefined,
    int gain=0,
    csdrplay.sdrplay_api_If_kHzT if_type=csdrplay.sdrplay_api_IF_Undefined,
    csdrplay.sdrplay_api_LoModeT lo_mode=csdrplay.sdrplay_api_LO_Undefined,
    int lna_state=-1,        # -1 means no change
):
    cdef error_t err

    if g_device.dev == NULL or g_devParams == NULL:
        return csdrplay.sdrplay_api_NotInitialised

    # First write the parameters into the parameter tree
    if reason_flags & csdrplay.sdrplay_api_Update_Dev_Fs:
        g_devParams.devParams.fsFreq.fsHz = sample_rate

    if reason_flags & csdrplay.sdrplay_api_Update_Tuner_Frf:
        g_devParams.rxChannelA.tunerParams.rfFreq.rfHz = frequency

    if reason_flags & csdrplay.sdrplay_api_Update_Tuner_BwType and bw_type != csdrplay.sdrplay_api_BW_Undefined:
        g_devParams.rxChannelA.tunerParams.bwType = bw_type

    if reason_flags & csdrplay.sdrplay_api_Update_Tuner_IfType and if_type != csdrplay.sdrplay_api_IF_Undefined:
        g_devParams.rxChannelA.tunerParams.ifType = if_type

    if reason_flags & csdrplay.sdrplay_api_Update_Tuner_LoMode and lo_mode != csdrplay.sdrplay_api_LO_Undefined:
        g_devParams.rxChannelA.tunerParams.loMode = lo_mode

    if reason_flags & csdrplay.sdrplay_api_Update_Tuner_Gr:
        if gain != 0:  # The input is "gain reduction" (gRdB)
            g_devParams.rxChannelA.tunerParams.gain.gRdB = gain
        if lna_state != -1:
            g_devParams.rxChannelA.tunerParams.gain.LNAstate = lna_state

    # Then apply them all at once
    err = csdrplay.sdrplay_api_Update(g_device.dev, g_tuner, <csdrplay.sdrplay_api_ReasonForUpdateT> reason_flags, csdrplay.sdrplay_api_Update_Ext1_None)
    return err

cpdef error_t close_stream() noexcept nogil:
    global reset_rx
    if g_device.dev == NULL:
        return csdrplay.sdrplay_api_NotInitialised
    reset_rx = True
    return csdrplay.sdrplay_api_Uninit(g_device.dev)
