from libcpp cimport bool

cdef extern from "lime/LimeSuite.h":
    ctypedef double float_type
    const int LMS_SUCCESS = 0

    ctypedef void lms_device_t
    ctypedef char lms_info_str_t[256]

    int LMS_GetDeviceList(lms_info_str_t *dev_list)
    int LMS_Open(lms_device_t ** device, lms_info_str_t info, void*args)
    int LMS_Close(lms_device_t *device)
    int LMS_Disconnect(lms_device_t *device)
    bool LMS_IsOpen(lms_device_t *device, int port)

    const bool LMS_CH_TX = True
    const bool LMS_CH_RX = False

    ctypedef struct lms_range_t:
        float_type min  # Minimum allowed value
        float_type max  # Minimum allowed value
        float_type step  # Minimum value step

    ctypedef enum lms_testsig_t:
        LMS_TESTSIG_NONE = 0  # Disable test signals. Return to normal operation
        LMS_TESTSIG_NCODIV8  # Test signal from NCO half scale
        LMS_TESTSIG_NCODIV4  # Test signal from NCO half scale
        LMS_TESTSIG_NCODIV8F  # Test signal from NCO full scale
        LMS_TESTSIG_NCODIV4F  # Test signal from NCO full scale
        LMS_TESTSIG_DC  # DC test signal

    int LMS_Init(lms_device_t *device)
    int LMS_GetNumChannels(lms_device_t *device, bool dir_tx)
    int LMS_EnableChannel(lms_device_t *device, bool dir_tx, size_t chan, bool enabled)

    int LMS_SetSampleRate(lms_device_t *device, float_type rate, size_t oversample)
    int LMS_GetSampleRate(lms_device_t *device, bool dir_tx, size_t chan, float_type *host_Hz, float_type *rf_Hz)
    int LMS_GetSampleRateRange(lms_device_t *device, bool dir_tx, lms_range_t *range)

    int LMS_SetLOFrequency(lms_device_t *device, bool dir_tx, size_t chan, float_type frequency)
    int LMS_GetLOFrequency(lms_device_t *device, bool dir_tx, size_t chan, float_type *frequency)
    int LMS_GetLOFrequencyRange(lms_device_t *device, bool dir_tx, lms_range_t *range)

    int LMS_SetNormalizedGain(lms_device_t *device, bool dir_tx, size_t chan, float_type gain)
    int LMS_GetNormalizedGain(lms_device_t *device, bool dir_tx, size_t chan, float_type *gain)

    int LMS_SetLPFBW(lms_device_t *device, bool dir_tx, size_t chan, float_type bandwidth)
    int LMS_GetLPFBW(lms_device_t *device, bool dir_tx, size_t chan, float_type *bandwidth)
    int LMS_GetLPFBWRange(lms_device_t *device, bool dir_tx, lms_range_t *range)
    int LMS_SetLPF(lms_device_t *device, bool dir_tx, size_t chan, bool enabled)
    int LMS_SetGFIRLPF(lms_device_t *device, bool dir_tx, size_t chan, bool enabled, float_type bandwidth)
    int LMS_Calibrate(lms_device_t *device, bool dir_tx, size_t chan, double bw, unsigned flags)

    ctypedef char lms_name_t[16]
    int LMS_GetAntennaList(lms_device_t *device, bool dir_tx, size_t chan, lms_name_t *list)
    int LMS_SetAntenna(lms_device_t *device, bool dir_tx, size_t chan, size_t index)
    int LMS_GetAntenna(lms_device_t *device, bool dir_tx, size_t chan)
    int LMS_GetAntennaBW(lms_device_t *device, bool dir_tx, size_t chan, size_t index, lms_range_t *range)

    int LMS_GetChipTemperature(lms_device_t *dev, size_t ind, float_type *temp)
