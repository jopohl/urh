ctypedef fused iq:
    char
    unsigned char
    short
    unsigned short
    float

ctypedef iq[:, ::1] IQ

from libc.stdint cimport uint64_t, uint8_t, int64_t

cpdef uint64_t bit_array_to_number(uint8_t[:] bits, int64_t end, int64_t start=*) nogil