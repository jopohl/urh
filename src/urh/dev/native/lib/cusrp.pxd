from libcpp.string cimport string
from libcpp.vector cimport vector
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
    uhd_error uhd_rx_metadata_free(uhd_rx_metadata_handle* handle)
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


cdef extern from "uhd/types/string_vector.h":
    ctypedef struct uhd_string_vector_t:
        vector[string] string_vector_cpp
        string last_error

    ctypedef uhd_string_vector_t* uhd_string_vector_handle;
    uhd_error uhd_string_vector_make(uhd_string_vector_handle *h)
    uhd_error uhd_string_vector_free(uhd_string_vector_handle *h)

cdef extern from "uhd/usrp/usrp.h":
    struct uhd_rx_streamer
    struct uhd_tx_streamer

    ctypedef uhd_rx_streamer* uhd_rx_streamer_handle
    ctypedef uhd_tx_streamer* uhd_tx_streamer_handle
    
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
        bool stream_now;
        # If not now, then full seconds into future to stream
        time_t time_spec_full_secs;
        # If not now, then fractional seconds into future to stream
        double time_spec_frac_secs;


    uhd_error uhd_usrp_find(const char* args, uhd_string_vector_handle *strings_out)

    uhd_error uhd_rx_streamer_make(uhd_rx_streamer_handle *h)
    uhd_error uhd_rx_streamer_free(uhd_rx_streamer_handle *h)
    uhd_error uhd_rx_streamer_num_channels(uhd_rx_streamer_handle h, size_t *num_channels_out)
    uhd_error uhd_rx_streamer_max_num_samps(uhd_rx_streamer_handle h, size_t *max_num_samps_out)
    uhd_error uhd_rx_streamer_recv(uhd_rx_streamer_handle h, void** buffs, size_t samps_per_buff,
                                   uhd_rx_metadata_handle *md, double timeout, bool one_packet, size_t *items_recvd)
    uhd_error uhd_rx_streamer_issue_stream_cmd(uhd_rx_streamer_handle h, const uhd_stream_cmd_t *stream_cmd)
    uhd_error uhd_rx_streamer_last_error(uhd_rx_streamer_handle h, char* error_out, size_t strbuffer_len)
