from libcpp cimport bool

ctypedef unsigned int  uint32_t
ctypedef unsigned long long uint64_t

cdef extern from "lime/LimeSuite.h":
    ctypedef double float_type
    int LMS_SUCCESS = 0

    ctypedef void lms_device_t
    ctypedef char lms_info_str_t[256]

    int LMS_GetDeviceList(lms_info_str_t *dev_list)
    int LMS_Open(lms_device_t ** device, lms_info_str_t info, void*args)
    int LMS_Close(lms_device_t *device)

    bool LMS_CH_TX = True
    bool LMS_CH_RX = False

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
    int LMS_Reset(lms_device_t *device)
    int LMS_Synchronize(lms_device_t *dev, bool to_chip)
    int LMS_GetNumChannels(lms_device_t *device, bool dir_tx)
    int LMS_EnableChannel(lms_device_t *device, bool dir_tx, size_t chan, bool enabled)

    int LMS_SaveConfig(lms_device_t *device, const char *filename)
    int LMS_LoadConfig(lms_device_t *device, const char *filename)

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

    int LMS_SetNCOFrequency(lms_device_t *device, bool dir_tx, size_t chan, const float_type *freq, float_type pho)
    int LMS_GetNCOFrequency(lms_device_t *device, bool dir_tx, size_t chan, float_type *freq, float_type *pho)

    int LMS_GetClockFreq(lms_device_t *dev, size_t clk_id, float_type *freq)
    int LMS_SetClockFreq(lms_device_t *dev, size_t clk_id, float_type freq)

    ctypedef char lms_name_t[16]
    int LMS_GetAntennaList(lms_device_t *device, bool dir_tx, size_t chan, lms_name_t *list)
    int LMS_SetAntenna(lms_device_t *device, bool dir_tx, size_t chan, size_t index)
    int LMS_GetAntenna(lms_device_t *device, bool dir_tx, size_t chan)
    int LMS_GetAntennaBW(lms_device_t *device, bool dir_tx, size_t chan, size_t index, lms_range_t *range)

    int LMS_GetChipTemperature(lms_device_t *dev, size_t ind, float_type *temp)

    ctypedef struct lms_stream_meta_t:
        # Timestamp is a value of HW counter with a tick based on sample rate.
        # In RX: time when the first sample in the returned buffer was received
        # In TX: time when the first sample in the submitted buffer should be send
        uint64_t timestamp

        # In TX: wait for the specified HW timestamp before broadcasting data over the air
        # In RX: wait for the specified HW timestamp before starting to receive samples
        bool waitForTimestamp

        # Indicates the end of send/receive transaction. Discards data remainder
        # in buffer (if there is any) in RX or flushes transfer buffer in TX (even
        # if the buffer is not full yet)
        bool flushPartialPacket

    ctypedef enum dataFmt_t:
        LMS_FMT_F32 "lms_stream_t::LMS_FMT_F32" = 0
        LMS_FMT_I16 "lms_stream_t::LMS_FMT_I16"
        LMS_FMT_I12 "lms_stream_t::LMS_FMT_I12"

    ctypedef struct lms_stream_t:
        # Stream handle. Should not be modified manually. Assigned by LMS_SetupStream()
        size_t handle

        # Indicates whether stream is TX (true) or RX (false)
        bool isTx

        # Channel number. Starts at 0.
        uint32_t channel

        # FIFO size (in samples) used by stream.
        uint32_t fifoSize

        # Parameter for controlling configuration bias toward low latency or high data throughput range [0,1.0].
        # 0 - lowest latency, usually results in lower throughput
        # 1 - higher throughput, usually results in higher latency
        float throughputVsLatency

        dataFmt_t dataFmt

    ctypedef struct lms_stream_status_t:
        bool active  # Indicates whether the stream is currently active
        uint32_t fifoFilledCount  # Number of samples in FIFO buffer
        uint32_t fifoSize  # Size of FIFO buffer
        uint32_t underrun  # FIFO underrun count
        uint32_t overrun  # FIFO overrun count
        uint32_t droppedPackets  # Number of dropped packets by HW
        float_type sampleRate  # Sampling rate of the stream
        float_type linkRate  # Combined data rate of all stream of the same direction (TX or RX)
        uint64_t timestamp  # Current HW timestamp

    int LMS_SetupStream(lms_device_t *device, lms_stream_t *stream)
    int LMS_DestroyStream(lms_device_t *device, lms_stream_t *stream)
    int LMS_StartStream(lms_stream_t *stream)
    int LMS_StopStream(lms_stream_t *conf)
    int LMS_GetStreamStatus(lms_stream_t *stream, lms_stream_status_t*status)
    int LMS_RecvStream(lms_stream_t *stream, void *samples, size_t sample_count, lms_stream_meta_t *meta,
                       unsigned timeout_ms)
    int LMS_SendStream(lms_stream_t *stream, const void *samples, size_t sample_count, const lms_stream_meta_t *meta,
                       unsigned timeout_ms)

    const char* LMS_GetLastErrorMessage()
