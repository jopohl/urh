from urh.dev.native.lib.cusrp cimport *
import numpy as np
# noinspection PyUnresolvedReferences
cimport numpy as np
from libc.stdlib cimport malloc, free
# noinspection PyUnresolvedReferences
from cython.view cimport array as cvarray  # needed for converting of malloc array to python array

import cython
from libc.string cimport memcpy

cdef uhd_usrp_handle _c_device
cdef uhd_rx_streamer_handle rx_streamer_handle
cdef uhd_tx_streamer_handle tx_streamer_handle
cdef uhd_rx_metadata_handle rx_metadata_handle
cdef uhd_tx_metadata_handle tx_metadata_handle

cdef bint IS_TX = False
cdef size_t CHANNEL = 0
cdef size_t max_num_rx_samples = 300
cdef size_t max_num_tx_samples = 300

cpdef set_tx(bint is_tx):
    global IS_TX
    IS_TX = is_tx

cpdef set_channel(size_t channel):
    global CHANNEL
    CHANNEL = channel

cpdef uhd_error open(str device_args):
    if not device_args:
        device_args = ""
    py_byte_string = device_args.encode('UTF-8')
    cdef char* dev_args = py_byte_string

    return uhd_usrp_make(&_c_device, dev_args)

cpdef uhd_error close():
    return uhd_usrp_free(&_c_device)

cpdef uhd_error set_subdevice(str markup, size_t mboard=0):
    if not markup:
        return <uhd_error>0

    py_byte_string = markup.encode("UTF-8")
    cdef char* c_markup = py_byte_string

    cdef uhd_subdev_spec_handle subdev_handle
    cdef subdev_make_error = uhd_subdev_spec_make(&subdev_handle, c_markup)
    if subdev_make_error != 0:
        return subdev_make_error

    if IS_TX:
        return uhd_usrp_set_tx_subdev_spec(_c_device, subdev_handle, mboard)
    else:
        return uhd_usrp_set_rx_subdev_spec(_c_device, subdev_handle, mboard)

cpdef uhd_error setup_stream():
    cdef uhd_stream_args_t stream_args
    # https://files.ettus.com/manual/structuhd_1_1stream__args__t.html
    stream_args.cpu_format = "fc32"
    stream_args.otw_format = "sc16"
    stream_args.args = ""
    cdef size_t channel = 0
    stream_args.channel_list = &channel
    stream_args.n_channels = 1

    cdef size_t num_channels = 0

    if not IS_TX:
        uhd_rx_streamer_make(&rx_streamer_handle)
        uhd_usrp_get_rx_stream(_c_device, &stream_args, rx_streamer_handle)
        uhd_rx_streamer_num_channels(rx_streamer_handle, &num_channels)
    else:
        uhd_tx_streamer_make(&tx_streamer_handle)
        uhd_usrp_get_tx_stream(_c_device, &stream_args, tx_streamer_handle)
        uhd_tx_streamer_num_channels(tx_streamer_handle, &num_channels)

cpdef uhd_error start_stream(int num_samples):
    if IS_TX:
        uhd_tx_streamer_max_num_samps(tx_streamer_handle, &max_num_tx_samples)
        return uhd_tx_metadata_make(&tx_metadata_handle, False, 0, 0.1, True, False)

    cdef uhd_stream_cmd_t stream_cmd
    stream_cmd.stream_mode = uhd_stream_mode_t.UHD_STREAM_MODE_START_CONTINUOUS
    stream_cmd.num_samps = 0
    stream_cmd.stream_now = True

    uhd_rx_streamer_max_num_samps(rx_streamer_handle, &max_num_rx_samples)

    uhd_rx_metadata_make(&rx_metadata_handle)
    return uhd_rx_streamer_issue_stream_cmd(rx_streamer_handle, &stream_cmd)

cpdef uhd_error stop_stream():
    if IS_TX:
        return uhd_tx_metadata_free(&tx_metadata_handle)

    cdef uhd_stream_cmd_t stream_cmd
    stream_cmd.stream_mode = uhd_stream_mode_t.UHD_STREAM_MODE_STOP_CONTINUOUS
    uhd_rx_metadata_free(&rx_metadata_handle)
    return uhd_rx_streamer_issue_stream_cmd(rx_streamer_handle, &stream_cmd)

cpdef uhd_error destroy_stream():
    if not IS_TX:
        return uhd_rx_streamer_free(&rx_streamer_handle)
    else:
        return uhd_tx_streamer_free(&tx_streamer_handle)

cpdef uhd_error recv_stream(connection, int num_samples):
    num_samples = (<int>(num_samples / max_num_rx_samples) + 1) * max_num_rx_samples
    cdef float* result = <float*>malloc(num_samples * 2 * sizeof(float))
    if not result:
        raise MemoryError()

    cdef int current_index = 0
    cdef int i = 0


    cdef float* buff = <float *>malloc(max_num_rx_samples * 2 * sizeof(float))
    if not buff:
        raise MemoryError()

    cdef void ** buffs = <void **> &buff
    cdef size_t items_received


    try:
        while current_index < 2*num_samples:
            uhd_rx_streamer_recv(rx_streamer_handle, buffs, max_num_rx_samples, &rx_metadata_handle, 3.0, False, &items_received)
            memcpy(&result[current_index], &buff[0], 2 * items_received * sizeof(float))
            #for i in range(current_index, current_index+2*items_received):
            #    result[i] = buff[i-current_index]

            current_index += 2*items_received

        connection.send_bytes(<float[:2*num_samples]>result)
    finally:
        free(buff)
        free(result)

@cython.boundscheck(False)
@cython.initializedcheck(False)
@cython.wraparound(False)
cpdef uhd_error send_stream(float[::1] samples):
    if len(samples) == 1 and samples[0] == 0:
        # Fill with zeros. Use some more zeros to prevent underflows
        samples = np.zeros(8 * max_num_tx_samples, dtype=np.float32)

    cdef unsigned long i, index = 0
    cdef size_t num_samps_sent = 0
    cdef size_t sample_count = len(samples)

    cdef float* buff = <float *>malloc(max_num_tx_samples * 2 * sizeof(float))
    if not buff:
        raise MemoryError()

    cdef const void ** buffs = <const void **> &buff

    try:
        for i in range(0, sample_count):
            buff[index] = samples[i]
            index += 1
            if index >= 2*max_num_tx_samples:
                index = 0
                uhd_tx_streamer_send(tx_streamer_handle, buffs, max_num_tx_samples,
                                     &tx_metadata_handle, 0.1, &num_samps_sent)

        uhd_tx_streamer_send(tx_streamer_handle, buffs, int(index / 2), &tx_metadata_handle, 0.1, &num_samps_sent)
    finally:
        free(buff)


cpdef str get_device_representation():
    cdef size_t size = 3000
    cdef char * result = <char *> malloc(size * sizeof(char))
    uhd_usrp_get_pp_string(_c_device, result, size)
    return result.decode("UTF-8")

cpdef uhd_error set_sample_rate(double sample_rate):
    if IS_TX:
        return uhd_usrp_set_tx_rate(_c_device, sample_rate, CHANNEL)
    else:
        return uhd_usrp_set_rx_rate(_c_device, sample_rate, CHANNEL)

cpdef uhd_error set_bandwidth(double bandwidth):
    if IS_TX:
        return uhd_usrp_set_tx_bandwidth(_c_device, bandwidth, CHANNEL)
    else:
        return uhd_usrp_set_rx_bandwidth(_c_device, bandwidth, CHANNEL)

cpdef uhd_error set_rf_gain(double normalized_gain):
    """
    Normalized gain must be between 0 and 1
    :param normalized_gain: 
    :return: 
    """
    if IS_TX:
        return uhd_usrp_set_normalized_tx_gain(_c_device, normalized_gain, CHANNEL)
    else:
        return uhd_usrp_set_normalized_rx_gain(_c_device, normalized_gain, CHANNEL)

cpdef uhd_error set_center_freq(double center_freq):
    cdef uhd_tune_request_t tune_request = {"target_freq": center_freq,
                                            "rf_freq_policy": uhd_tune_request_policy_t.UHD_TUNE_REQUEST_POLICY_AUTO,
                                            "dsp_freq_policy": uhd_tune_request_policy_t.UHD_TUNE_REQUEST_POLICY_AUTO}

    cdef uhd_tune_result_t tune_result
    if IS_TX:
        result = uhd_usrp_set_tx_freq(_c_device, &tune_request, CHANNEL, &tune_result)
    else:
        result = uhd_usrp_set_rx_freq(_c_device, &tune_request, CHANNEL, &tune_result)

    return result

cpdef str get_last_error():
    if _c_device is NULL:
        return "Could not retrieve more detailed error message from device."

    cdef char * error_msg = <char *> malloc(1024 * sizeof(char))
    uhd_usrp_last_error(_c_device, error_msg, 1024)

    try:
        error_msg_py = <bytes>error_msg
        return error_msg_py.decode("UTF-8")
    finally:
        free(error_msg)

cpdef str get_antenna():
    cdef char* antenna = <char *> malloc(512 * sizeof(char))
    if IS_TX:
        uhd_usrp_get_tx_antenna(_c_device, CHANNEL, antenna, 512)
    else:
        uhd_usrp_get_rx_antenna(_c_device, CHANNEL, antenna, 512)

    try:
        antenna_py = <bytes>antenna
        return antenna_py.decode("UTF-8")
    finally:
        free(antenna)

cpdef uhd_error set_antenna(int index):
    cdef list antennas = get_antennas()
    if index < 0 or index >= len(antennas):
        return <uhd_error>4711

    cdef bytes antenna_py_bytes = antennas[index].encode("UTF-8")
    cdef char* antenna = antenna_py_bytes

    if IS_TX:
        return uhd_usrp_set_tx_antenna(_c_device, antenna, CHANNEL)
    else:
        return uhd_usrp_set_rx_antenna(_c_device, antenna, CHANNEL)

cpdef list get_antennas():
    cdef uhd_string_vector_handle h
    cdef size_t i, num_antennas
    cdef char* vector_str_item = <char *> malloc(512 * sizeof(char))

    uhd_string_vector_make(&h)

    result = []

    if IS_TX:
        uhd_usrp_get_tx_antennas(_c_device, CHANNEL, &h)
    else:
        uhd_usrp_get_rx_antennas(_c_device, CHANNEL, &h)

    uhd_string_vector_size(h, &num_antennas)
    for i in range(num_antennas):
        uhd_string_vector_at(h, i, vector_str_item, 512)
        antenna_str = vector_str_item.decode("UTF-8")
        if antenna_str not in result:
            result.append(antenna_str)

    free(vector_str_item)
    uhd_string_vector_free(&h)

    return result

cpdef list find_devices(str args):
    py_byte_string = args.encode('UTF-8')
    cdef char* dev_args = py_byte_string
    cdef uhd_string_vector_handle h
    uhd_string_vector_make(&h)
    uhd_usrp_find(dev_args, &h)
    cdef size_t i, num_devices = 0
    uhd_string_vector_size(h, &num_devices)
    cdef char* vector_str_item = <char *> malloc(512 * sizeof(char))

    result = []

    for i in range(num_devices):
        uhd_string_vector_at(h, i, vector_str_item, 512)
        device_str = vector_str_item.decode("UTF-8")
        if device_str not in result:
            result.append(device_str)

    free(vector_str_item)
    uhd_string_vector_free(&h)

    return result
