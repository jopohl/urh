ctypedef fused iq:
    char
    unsigned char
    short
    unsigned short
    float

ctypedef iq[:, ::1] IQ