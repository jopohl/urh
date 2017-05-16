from cusrp cimport *
import numpy as np
# noinspection PyUnresolvedReferences
cimport numpy as np
from libc.stdlib cimport malloc
# noinspection PyUnresolvedReferences
from cython.view cimport array as cvarray  # needed for converting of malloc array to python array


from urh.util.Logger import logger

np.import_array()

cdef uhd_usrp_handle _c_device
cdef uhd_rx_streamer_handle rx_streamer_handle

cpdef bool IS_TX = False

cpdef set_tx(bool is_tx):
    global IS_TX
    IS_TX = is_tx

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

cpdef uhd_error setup_stream():
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

    cdef size_t num_channels = 0

    if not IS_TX:
        uhd_rx_streamer_make(&rx_streamer_handle)
        uhd_usrp_get_rx_stream(_c_device, &stream_args, rx_streamer_handle)


        uhd_rx_streamer_num_channels(rx_streamer_handle, &num_channels)
        print("Num channels", num_channels)


    else:
        raise NotImplementedError("ToDo")

cpdef uhd_error destroy_stream():
    if not IS_TX:
        return  uhd_rx_streamer_free(&rx_streamer_handle)
    else:
        raise NotImplementedError("ToDo")

cpdef uhd_error recv_stream(connection, size_t num_samples):
    cdef uhd_stream_cmd_t stream_cmd
    stream_cmd.stream_mode = uhd_stream_mode_t.UHD_STREAM_MODE_NUM_SAMPS_AND_DONE
    stream_cmd.num_samps = num_samples
    stream_cmd.stream_now = 1

    cdef float* buff = <float *>malloc(num_samples * 2 * sizeof(float))
    cdef void ** buffs = <void **> &buff

    cdef uhd_rx_metadata_handle metadata_handle
    uhd_rx_metadata_make(&metadata_handle)

    cdef size_t items_received

    uhd_rx_streamer_issue_stream_cmd(rx_streamer_handle, &stream_cmd)
    uhd_rx_streamer_recv(rx_streamer_handle, buffs, num_samples, &metadata_handle, 1, 0, &items_received)

    uhd_rx_metadata_free(&metadata_handle)

    if items_received > 0:
        connection.send_bytes(<float[:2*items_received]>buff)
    else:
        logger.warning("USRP: Failed to receive stream")


cpdef str get_device_representation():
    cdef size_t size = 3000
    cdef char * result = <char *> malloc(size * sizeof(char))
    uhd_usrp_get_pp_string(_c_device, result, size)
    return result.decode("UTF-8")

