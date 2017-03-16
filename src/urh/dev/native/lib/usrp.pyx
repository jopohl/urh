cimport cusrp
# noinspection PyUnresolvedReferences
import numpy as np
cimport numpy as np

cpdef find_devices(device_args):
    """
    Find all connected USRP devices.
    """

    cdef cusrp.uhd_string_vector_handle output
    cusrp.uhd_string_vector_make(&output)

    py_byte_string = device_args.encode('UTF-8')
    cdef char* args = py_byte_string

    ret_code = cusrp.uhd_usrp_find(args, &output)
    result = output.string_vector_cpp
    cusrp.uhd_string_vector_free(&output)

    return ret_code, result

def receive(device_args):
    py_byte_string = device_args.encode('UTF-8')
    cdef char* dev_args = py_byte_string

    cdef cusrp.uhd_usrp_handle usrp_handle
    cdef cusrp.uhd_rx_streamer_handle rx_streamer_handle
    cusrp.uhd_rx_streamer_make(&rx_streamer_handle)
    print("Made rx_streame handler")

    cdef cusrp.uhd_stream_args_t stream_args
    # https://files.ettus.com/manual/structuhd_1_1stream__args__t.html
    byte_string_cpu_format = "fc32".encode("UTF-8")
    cdef char* cpu_format = byte_string_cpu_format
    stream_args.cpu_format = cpu_format
    cusrp.uhd_usrp_make(&usrp_handle, dev_args)
    print("Called usrp_make")

    cusrp.uhd_usrp_get_rx_stream(usrp_handle, &stream_args, rx_streamer_handle)
    print("Called get_rx_stream")

    cdef size_t max_num_samps_out
    cusrp.uhd_rx_streamer_max_num_samps(rx_streamer_handle, &max_num_samps_out)
    print("Max num samps:", max_num_samps_out)

    cusrp.uhd_usrp_free(&usrp_handle)
    cusrp.uhd_rx_streamer_free(&rx_streamer_handle)
