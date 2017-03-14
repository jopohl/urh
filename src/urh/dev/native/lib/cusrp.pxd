from libcpp.string cimport string
from libcpp.vector cimport vector

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
     uhd_error uhd_usrp_find(const char* args, uhd_string_vector_handle *strings_out)

