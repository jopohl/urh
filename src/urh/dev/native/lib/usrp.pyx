from cusrp cimport *
import numpy as np
# noinspection PyUnresolvedReferences
cimport numpy as np
from libc.stdlib cimport malloc
# noinspection PyUnresolvedReferences
from cython.view cimport array as cvarray  # needed for converting of malloc array to python array

from libc.string cimport memcpy

np.import_array()

cdef uhd_usrp_handle _c_device
cdef uhd_rx_streamer_handle rx_streamer_handle
cdef uhd_tx_streamer_handle tx_streamer_handle
cdef uhd_rx_metadata_handle rx_metadata_handle
cdef uhd_tx_metadata_handle tx_metadata_handle

cpdef bint IS_TX = False
cpdef size_t CHANNEL = 0
cdef size_t max_num_rx_samples = 300
cdef size_t max_num_tx_samples = 300

cpdef set_tx(bint is_tx):
    global IS_TX
    IS_TX = is_tx

cpdef set_channel(size_t channel):
    global CHANNEL
    CHANNEL = channel

cpdef uhd_error open(str device_args):
    py_byte_string = device_args.encode('UTF-8')
    cdef char* dev_args = py_byte_string

    return uhd_usrp_make(&_c_device, dev_args)

cpdef uhd_error close():
    return uhd_usrp_free(&_c_device)

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
        print("Num channels", num_channels)
    else:
        uhd_tx_streamer_make(&tx_streamer_handle)
        uhd_usrp_get_tx_stream(_c_device, &stream_args, tx_streamer_handle)
        uhd_tx_streamer_num_channels(tx_streamer_handle, &num_channels)
        print("Num channels", num_channels)

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
    cdef int current_index = 0
    cdef int i = 0


    cdef float* buff = <float *>malloc(max_num_rx_samples * 2 * sizeof(float))
    cdef void ** buffs = <void **> &buff
    cdef size_t items_received


    while current_index < 2*num_samples:
        uhd_rx_streamer_recv(rx_streamer_handle, buffs, max_num_rx_samples, &rx_metadata_handle, 3.0, False, &items_received)
        memcpy(&result[current_index], &buff[0], 2 * items_received * sizeof(float))
        #for i in range(current_index, current_index+2*items_received):
        #    result[i] = buff[i-current_index]

        current_index += 2*items_received

    connection.send_bytes(<float[:2*num_samples]>result)

cpdef uhd_error send_stream(float[::1] samples):
    cdef size_t sample_count = len(samples)
    cdef int i
    cdef int index = 0
    cdef size_t num_samps_sent = 0

    cdef float* buff = <float *>malloc(max_num_tx_samples * 2 * sizeof(float))
    cdef const void ** buffs = <const void **> &buff

    for i in range(0, sample_count):
        buff[index] = samples[i]
        index += 1
        if index >= 2*max_num_tx_samples:
            index = 0
            uhd_tx_streamer_send(tx_streamer_handle, buffs, max_num_tx_samples, &tx_metadata_handle, 0.1, &num_samps_sent)

    uhd_tx_streamer_send(tx_streamer_handle, buffs, int(index / 2), &tx_metadata_handle, 0.1, &num_samps_sent)


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
    cdef uhd_tune_request_t tune_request
    tune_request.target_freq = center_freq
    tune_request.rf_freq_policy = uhd_tune_request_policy_t.UHD_TUNE_REQUEST_POLICY_AUTO
    tune_request.dsp_freq_policy = uhd_tune_request_policy_t.UHD_TUNE_REQUEST_POLICY_AUTO

    cdef uhd_tune_result_t tune_result
    if IS_TX:
        result = uhd_usrp_set_tx_freq(_c_device, &tune_request, CHANNEL, &tune_result)
    else:
        result = uhd_usrp_set_rx_freq(_c_device, &tune_request, CHANNEL, &tune_result)

    print("USRP target frequency", tune_result.target_rf_freq, "actual frequency", tune_result.actual_rf_freq)

    return result

cpdef str get_last_error():
    cdef char * error_msg = <char *> malloc(200 * sizeof(char))

    if IS_TX:
        uhd_tx_streamer_last_error(tx_streamer_handle, error_msg, 200)
    else:
        uhd_rx_streamer_last_error(rx_streamer_handle, error_msg, 200)
    error_msg_py = error_msg.decode("UTF-8")
    return error_msg_py
