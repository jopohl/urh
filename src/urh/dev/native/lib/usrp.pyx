from cusrp cimport *
# noinspection PyUnresolvedReferences
import numpy as np
cimport numpy as np
from libc.stdlib cimport malloc, free

np.import_array()

cdef uhd_usrp_handle _c_device

cpdef find_devices(device_args):
    """
    Find all connected USRP devices.
    """

    cdef uhd_string_vector_handle output
    uhd_string_vector_make(&output)

    py_byte_string = device_args.encode('UTF-8')
    cdef char* args = py_byte_string

    ret_code = uhd_usrp_find(args, &output)
    result = output.string_vector_cpp
    uhd_string_vector_free(&output)

    return ret_code, result

cpdef uhd_error open(str device_args):
    py_byte_string = device_args.encode('UTF-8')
    cdef char* dev_args = py_byte_string

    return uhd_usrp_make(&_c_device, dev_args)

cpdef uhd_error close():
    return uhd_usrp_free(&_c_device)


def receive(device_args):
    py_byte_string = device_args.encode('UTF-8')
    cdef char* dev_args = py_byte_string

    cdef uhd_usrp_handle usrp_handle
    cdef uhd_rx_streamer_handle rx_streamer_handle
    uhd_rx_streamer_make(&rx_streamer_handle)
    print("Made rx_streame handler")

    cdef uhd_stream_args_t stream_args

    # https://files.ettus.com/manual/structuhd_1_1stream__args__t.html
    byte_string_cpu_format = "fc32".encode("UTF-8")
    cdef char* cpu_format = byte_string_cpu_format
    stream_args.cpu_format = cpu_format
    byte_string_otw_format = "sc16".encode("UTF-8")
    cdef char* otw_format = byte_string_otw_format
    stream_args.otw_format = otw_format
    byte_string_other_stream_args = "".encode("UTF-8")
    cdef char* other_stream_args = byte_string_other_stream_args
    stream_args.args = other_stream_args
    cdef size_t channel = 0
    stream_args.channel_list = &channel
    stream_args.n_channels = 1

    cdef uhd_stream_cmd_t stream_cmd
    stream_cmd.stream_mode = uhd_stream_mode_t.UHD_STREAM_MODE_NUM_SAMPS_AND_DONE
    stream_cmd.num_samps = 363
    stream_cmd.stream_now = 1

    uhd_usrp_make(&usrp_handle, dev_args)
    print("Called usrp_make")

    uhd_usrp_get_rx_stream(usrp_handle, &stream_args, rx_streamer_handle)
    print("Called get_rx_stream")

    cdef size_t num_channels = 0
    uhd_rx_streamer_num_channels(rx_streamer_handle, &num_channels)
    print("Num channels", num_channels)

    cdef size_t max_num_samps_out
    uhd_rx_streamer_max_num_samps(rx_streamer_handle, &max_num_samps_out)
    print("Max num samps:", max_num_samps_out)



    cdef float* buff = <float *>malloc(max_num_samps_out * 2 * sizeof(float))
    buff[0] = 42
    cdef void ** buffs = <void **> &buff

    #cdef np.complex64_t[:] buffer = np.empty(max_num_samps_out, dtype=np.complex64)
    #cdef void ** buffs = <void **> malloc(buffer.shape[0]*sizeof(void *))
    #buffs[0] = <void *>buffer

    cdef uhd_rx_metadata_handle metadata_handle
    uhd_rx_metadata_make(&metadata_handle)

    cdef size_t items_received

    print("Buffer 0 before RX", buff[0])

    uhd_rx_streamer_issue_stream_cmd(rx_streamer_handle, &stream_cmd)
    uhd_rx_streamer_recv(rx_streamer_handle, buffs, max_num_samps_out, &metadata_handle, 1, 0, &items_received)

    print("Received items:", items_received)

    print("Buffer 0 after RX", buff[0])

    uhd_rx_streamer_free(&rx_streamer_handle)
    print("Freed rx streamer handler")
    uhd_rx_metadata_free(&metadata_handle)
    print("Freed metadata handle")
    uhd_usrp_free(&usrp_handle)
    print("Freed usrp handle")

