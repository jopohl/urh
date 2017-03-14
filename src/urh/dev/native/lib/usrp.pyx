cimport cusrp

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
