from libc.time cimport time_t

cdef extern from "uhd/types/metadata.h":
    struct uhd_rx_metadata_t
    struct uhd_tx_metadata_t
    struct uhd_async_metadata_t
    ctypedef uhd_rx_metadata_t* uhd_rx_metadata_handle
    ctypedef uhd_tx_metadata_t* uhd_tx_metadata_handle
    ctypedef uhd_async_metadata_t* uhd_async_metadata_handle

    ctypedef enum uhd_rx_metadata_error_code_t:
        # No error code associated with this metadata
        UHD_RX_METADATA_ERROR_CODE_NONE         = 0x0,
        # No packet received, implementation timed out
        UHD_RX_METADATA_ERROR_CODE_TIMEOUT      = 0x1,
        # A stream command was issued in the past
        UHD_RX_METADATA_ERROR_CODE_LATE_COMMAND = 0x2,
        # Expected another stream command
        UHD_RX_METADATA_ERROR_CODE_BROKEN_CHAIN = 0x4,
        # Overflow or sequence error
        UHD_RX_METADATA_ERROR_CODE_OVERFLOW     = 0x8,
        # Multi-channel alignment failed
        UHD_RX_METADATA_ERROR_CODE_ALIGNMENT    = 0xC,
        # The packet could not be parsed
        UHD_RX_METADATA_ERROR_CODE_BAD_PACKET   = 0xF


    uhd_error uhd_rx_metadata_make(uhd_rx_metadata_handle* handle)
    uhd_error uhd_tx_metadata_make(uhd_tx_metadata_handle* handle, bint has_time_spec, time_t full_secs, double frac_secs, bint start_of_burst, bint end_of_burst)
    uhd_error uhd_rx_metadata_free(uhd_rx_metadata_handle* handle)
    uhd_error uhd_tx_metadata_free(uhd_tx_metadata_handle* handle)
    uhd_error uhd_rx_metadata_to_pp_string(uhd_rx_metadata_handle h, char* pp_string_out, size_t strbuffer_len)

cdef extern from "uhd/error.h":
    ctypedef enum uhd_error:
        # No error thrown.
        UHD_ERROR_NONE = 0,
        # Invalid device arguments.
        UHD_ERROR_INVALID_DEVICE = 1,

        # See uhd::index_error.
        UHD_ERROR_INDEX = 10,
        # See uhd::key_error.
        UHD_ERROR_KEY = 11,

        # See uhd::not_implemented_error.
        UHD_ERROR_NOT_IMPLEMENTED = 20,
        # See uhd::usb_error.
        UHD_ERROR_USB = 21,

        # See uhd::io_error.
        UHD_ERROR_IO = 30,
        # See uhd::os_error.
        UHD_ERROR_OS = 31,

        # See uhd::assertion_error.
        UHD_ERROR_ASSERTION = 40,
        # See uhd::lookup_error.
        UHD_ERROR_LOOKUP = 41,
        # See uhd::type_error.
        UHD_ERROR_TYPE = 42,
        # See uhd::value_error.
        UHD_ERROR_VALUE = 43,
        # See uhd::runtime_error.
        UHD_ERROR_RUNTIME = 44,
        # See uhd::environment_error.
        UHD_ERROR_ENVIRONMENT = 45,
        # See uhd::system_error.
        UHD_ERROR_SYSTEM = 46,
        # See uhd::exception.
        UHD_ERROR_EXCEPT = 47,

        # A boost::exception was thrown.
        UHD_ERROR_BOOSTEXCEPT = 60,

        # A std::exception was thrown.
        UHD_ERROR_STDEXCEPT = 70,

        # An unknown error was thrown.
        UHD_ERROR_UNKNOWN = 100

cdef extern from "uhd/types/tune_request.h":
    ctypedef enum uhd_tune_request_policy_t:
        UHD_TUNE_REQUEST_POLICY_NONE   = 78
        UHD_TUNE_REQUEST_POLICY_AUTO   = 65
        UHD_TUNE_REQUEST_POLICY_MANUAL = 77

    ctypedef struct uhd_tune_request_t:
        double target_freq
        uhd_tune_request_policy_t rf_freq_policy
        double rf_freq
        uhd_tune_request_policy_t dsp_freq_policy
        double dsp_freq
        char* args

cdef extern from "uhd/types/tune_result.h":
    ctypedef struct uhd_tune_result_t:
        double clipped_rf_freq
        double target_rf_freq
        double actual_rf_freq
        double target_dsp_freq
        double actual_dsp_freq

cdef extern from "uhd/types/string_vector.h":
    ctypedef struct uhd_string_vector_t
    ctypedef uhd_string_vector_t* uhd_string_vector_handle;
    uhd_error uhd_string_vector_make(uhd_string_vector_handle *h)
    uhd_error uhd_string_vector_free(uhd_string_vector_handle *h)
    uhd_error uhd_string_vector_size(uhd_string_vector_handle h, size_t *size_out)
    uhd_error uhd_string_vector_at(uhd_string_vector_handle h, size_t index, char* value_out, size_t strbuffer_len)

cdef extern from "uhd/usrp/subdev_spec.h":
    struct uhd_subdev_spec_t
    ctypedef uhd_subdev_spec_t* uhd_subdev_spec_handle;
    uhd_error uhd_subdev_spec_make(uhd_subdev_spec_handle* h, const char* markup)

cdef extern from "uhd/usrp/usrp.h":
    struct uhd_rx_streamer
    struct uhd_tx_streamer
    struct uhd_usrp

    ctypedef uhd_rx_streamer* uhd_rx_streamer_handle
    ctypedef uhd_tx_streamer* uhd_tx_streamer_handle
    ctypedef uhd_usrp* uhd_usrp_handle

    ctypedef enum uhd_stream_mode_t:
        # Stream samples indefinitely
        UHD_STREAM_MODE_START_CONTINUOUS   = 97,
        # End continuous streaming
        UHD_STREAM_MODE_STOP_CONTINUOUS    = 111,
        # Stream some number of samples and finish
        UHD_STREAM_MODE_NUM_SAMPS_AND_DONE = 100,
        # Stream some number of samples but expect more
        UHD_STREAM_MODE_NUM_SAMPS_AND_MORE = 109

    ctypedef struct uhd_stream_cmd_t:
        # How streaming is issued to the device
        uhd_stream_mode_t stream_mode;
        # Number of samples
        size_t num_samps;
        # Stream now?
        bint stream_now;
        # If not now, then full seconds into future to stream
        time_t time_spec_full_secs;
        # If not now, then fractional seconds into future to stream
        double time_spec_frac_secs;

    ctypedef struct uhd_stream_args_t:
        # Format of host memory
        char* cpu_format;
        # Over-the-wire format
        char* otw_format;
        # Other stream args
        char* args;
        # Array that lists channels
        size_t* channel_list;
        # Number of channels
        int n_channels;

    uhd_error uhd_usrp_find(const char* args, uhd_string_vector_handle *strings_out)
    uhd_error uhd_usrp_make(uhd_usrp_handle *h, const char *args)
    uhd_error uhd_usrp_free(uhd_usrp_handle *h)
    uhd_error uhd_usrp_last_error(uhd_usrp_handle h, char* error_out, size_t strbuffer_len)
    uhd_error uhd_usrp_get_rx_stream(uhd_usrp_handle h, uhd_stream_args_t *stream_args, uhd_rx_streamer_handle h_out)
    uhd_error uhd_usrp_get_tx_stream(uhd_usrp_handle h, uhd_stream_args_t *stream_args, uhd_tx_streamer_handle h_out)

    uhd_error uhd_rx_streamer_make(uhd_rx_streamer_handle *h)
    uhd_error uhd_tx_streamer_make(uhd_tx_streamer_handle *h)
    uhd_error uhd_rx_streamer_free(uhd_rx_streamer_handle *h)
    uhd_error uhd_tx_streamer_free(uhd_tx_streamer_handle *h)
    uhd_error uhd_rx_streamer_num_channels(uhd_rx_streamer_handle h, size_t *num_channels_out)
    uhd_error uhd_tx_streamer_num_channels(uhd_tx_streamer_handle h, size_t *num_channels_out)
    uhd_error uhd_rx_streamer_max_num_samps(uhd_rx_streamer_handle h, size_t *max_num_samps_out)
    uhd_error uhd_tx_streamer_max_num_samps(uhd_tx_streamer_handle h, size_t *max_num_samps_out)
    uhd_error uhd_rx_streamer_recv(uhd_rx_streamer_handle h, void** buffs, size_t samps_per_buff,
                                   uhd_rx_metadata_handle *md, double timeout, bint one_packet, size_t *items_recvd)
    uhd_error uhd_tx_streamer_send(uhd_tx_streamer_handle h, const void **buffs, size_t samps_per_buff, uhd_tx_metadata_handle *md, double timeout, size_t *items_sent)
    uhd_error uhd_rx_streamer_issue_stream_cmd(uhd_rx_streamer_handle h, const uhd_stream_cmd_t *stream_cmd)
    uhd_error uhd_rx_streamer_last_error(uhd_rx_streamer_handle h, char* error_out, size_t strbuffer_len)
    uhd_error uhd_tx_streamer_last_error(uhd_tx_streamer_handle h, char* error_out, size_t strbuffer_len)

    uhd_error uhd_usrp_get_pp_string(uhd_usrp_handle h, char* pp_string_out, size_t strbuffer_len)

    uhd_error uhd_usrp_set_rx_rate(uhd_usrp_handle h, double rate,size_t chan)
    uhd_error uhd_usrp_get_rx_rate(uhd_usrp_handle h, size_t chan, double *rate_out)
    uhd_error uhd_usrp_set_tx_rate(uhd_usrp_handle h, double rate,size_t chan)
    uhd_error uhd_usrp_get_tx_rate(uhd_usrp_handle h, size_t chan, double *rate_out)

    uhd_error uhd_usrp_set_rx_freq(uhd_usrp_handle h, uhd_tune_request_t *tune_request, size_t chan, uhd_tune_result_t *tune_result)
    uhd_error uhd_usrp_get_rx_freq(uhd_usrp_handle h, size_t chan, double *freq_out)
    uhd_error uhd_usrp_set_tx_freq(uhd_usrp_handle h, uhd_tune_request_t *tune_request, size_t chan, uhd_tune_result_t *tune_result)
    uhd_error uhd_usrp_get_tx_freq(uhd_usrp_handle h, size_t chan, double *freq_out)

    uhd_error uhd_usrp_set_normalized_rx_gain(uhd_usrp_handle h, double gain, size_t chan)
    uhd_error uhd_usrp_get_normalized_rx_gain(uhd_usrp_handle h, size_t chan, double *gain_out)
    uhd_error uhd_usrp_set_normalized_tx_gain(uhd_usrp_handle h, double gain, size_t chan)
    uhd_error uhd_usrp_get_normalized_tx_gain(uhd_usrp_handle h, size_t chan, double *gain_out)

    uhd_error uhd_usrp_set_rx_bandwidth(uhd_usrp_handle h, double bandwidth, size_t chan)
    uhd_error uhd_usrp_get_rx_bandwidth(uhd_usrp_handle h, size_t chan, double *bandwidth_out)
    uhd_error uhd_usrp_set_tx_bandwidth(uhd_usrp_handle h, double bandwidth, size_t chan)
    uhd_error uhd_usrp_get_tx_bandwidth(uhd_usrp_handle h, size_t chan, double *bandwidth_out)

    uhd_error uhd_usrp_set_rx_antenna(uhd_usrp_handle h, const char* ant, size_t chan)
    uhd_error uhd_usrp_get_rx_antenna(uhd_usrp_handle h, size_t chan, char* ant_out, size_t strbuffer_len)
    uhd_error uhd_usrp_get_rx_antennas(uhd_usrp_handle h, size_t chan, uhd_string_vector_handle *antennas_out)
    uhd_error uhd_usrp_set_tx_antenna(uhd_usrp_handle h, const char* ant, size_t chan)
    uhd_error uhd_usrp_get_tx_antenna(uhd_usrp_handle h, size_t chan, char* ant_out, size_t strbuffer_len)
    uhd_error uhd_usrp_get_tx_antennas(uhd_usrp_handle h, size_t chan, uhd_string_vector_handle *antennas_out)

    uhd_error uhd_usrp_set_rx_subdev_spec(uhd_usrp_handle h, uhd_subdev_spec_handle subdev_spec, size_t mboard)
    uhd_error uhd_usrp_set_tx_subdev_spec(uhd_usrp_handle h, uhd_subdev_spec_handle subdev_spec, size_t mboard)
