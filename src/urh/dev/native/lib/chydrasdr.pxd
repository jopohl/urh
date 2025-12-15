ctypedef unsigned char uint8_t
ctypedef short int16_t
ctypedef unsigned short uint16_t
ctypedef unsigned int uint32_t
ctypedef unsigned long long uint64_t

cdef extern from "libhydrasdr/hydrasdr.h":
    enum hydrasdr_error:
        HYDRASDR_SUCCESS = 0
        HYDRASDR_TRUE = 1
        HYDRASDR_ERROR_INVALID_PARAM = -2
        HYDRASDR_ERROR_NOT_FOUND = -5
        HYDRASDR_ERROR_BUSY = -6
        HYDRASDR_ERROR_NO_MEM = -11
        HYDRASDR_ERROR_LIBUSB = -1000
        HYDRASDR_ERROR_THREAD = -1001
        HYDRASDR_ERROR_STREAMING_THREAD_ERR = -1002
        HYDRASDR_ERROR_STREAMING_STOPPED = -1003
        HYDRASDR_ERROR_OTHER = -9999

    enum hydrasdr_board_id:
        HYDRASDR_BOARD_ID_PROTO_HYDRASDR = 0
        HYDRASDR_BOARD_ID_INVALID = 0xFF

    enum hydrasdr_sample_type:
        HYDRASDR_SAMPLE_FLOAT32_IQ = 0    # 2 * 32bit float per sample
        HYDRASDR_SAMPLE_FLOAT32_REAL = 1  # 1 * 32bit float per sample
        HYDRASDR_SAMPLE_INT16_IQ = 2      # 2 * 16bit int per sample
        HYDRASDR_SAMPLE_INT16_REAL = 3    # 1 * 16bit int per sample
        HYDRASDR_SAMPLE_UINT16_REAL = 4   # 1 * 16bit unsigned int per sample
        HYDRASDR_SAMPLE_RAW = 5           # Raw packed samples from the device
        HYDRASDR_SAMPLE_END = 6           # Number of supported sample types

    struct hydrasdr_device

    ctypedef struct hydrasdr_transfer:
        hydrasdr_device* device
        void* ctx
        void* samples
        int sample_count
        uint64_t dropped_samples
        hydrasdr_sample_type sample_type

    ctypedef struct hydrasdr_read_partid_serialno_t:
        uint32_t part_id[2]
        uint32_t serial_no[4]

    ctypedef struct hydrasdr_lib_version_t:
        uint32_t major_version
        uint32_t minor_version
        uint32_t revision

    ctypedef int (*hydrasdr_sample_block_cb_fn)(hydrasdr_transfer* transfer)
    
    void hydrasdr_lib_version(hydrasdr_lib_version_t* lib_version)
    int hydrasdr_open_sn(hydrasdr_device** device, uint64_t serial_number)
    int hydrasdr_open(hydrasdr_device** device)
    int hydrasdr_close(hydrasdr_device* device)
    
    int hydrasdr_get_samplerates(hydrasdr_device* device, uint32_t* buffer, const uint32_t len)
    
    # Parameter samplerate can be either the index of a samplerate or directly its value in Hz within the list returned by hydrasdr_get_samplerates()
    int hydrasdr_set_samplerate(hydrasdr_device* device, uint32_t samplerate)
    
    int hydrasdr_set_conversion_filter_float32(hydrasdr_device* device, const float *kernel, const uint32_t len)
    int hydrasdr_set_conversion_filter_int16(hydrasdr_device* device, const int16_t *kernel, const uint32_t len)
    
    int hydrasdr_start_rx(hydrasdr_device* device, hydrasdr_sample_block_cb_fn callback, void* rx_ctx)
    int hydrasdr_stop_rx(hydrasdr_device* device)
    
    # return HYDRASDR_TRUE if success
    int hydrasdr_is_streaming(hydrasdr_device* device)
    
    int hydrasdr_si5351c_write(hydrasdr_device* device, uint8_t register_number, uint8_t value)
    int hydrasdr_si5351c_read(hydrasdr_device* device, uint8_t register_number, uint8_t* value)
    
    int hydrasdr_config_write(hydrasdr_device* device, const uint8_t page_index, const uint16_t length, unsigned char *data)
    int hydrasdr_config_read(hydrasdr_device* device, const uint8_t page_index, const uint16_t length, unsigned char *data)
    
    int hydrasdr_r82x_write(hydrasdr_device* device, uint8_t register_number, uint8_t value)
    int hydrasdr_r82x_read(hydrasdr_device* device, uint8_t register_number, uint8_t* value)
    
    int hydrasdr_board_id_read(hydrasdr_device* device, uint8_t* value)
    # Parameter length shall be at least 128bytes
    int hydrasdr_version_string_read(hydrasdr_device* device, char* version, uint8_t length)
    
    int hydrasdr_board_partid_serialno_read(hydrasdr_device* device, hydrasdr_read_partid_serialno_t* read_partid_serialno)
    
    int hydrasdr_set_sample_type(hydrasdr_device* device, hydrasdr_sample_type sample_type)
    
    # Parameter freq_hz shall be between 24000000(24MHz) and 1750000000(1.75GHz)
    int hydrasdr_set_freq(hydrasdr_device* device, const uint32_t freq_hz)
    
    # Parameter value shall be between 0 and 15
    int hydrasdr_set_lna_gain(hydrasdr_device* device, uint8_t value)
    
    # Parameter value shall be between 0 and 15
    int hydrasdr_set_mixer_gain(hydrasdr_device* device, uint8_t value)
    
    # Parameter value shall be between 0 and 15
    int hydrasdr_set_vga_gain(hydrasdr_device* device, uint8_t value)
    
    # Parameter value:
    # 0=Disable LNA Automatic Gain Control
    # 1=Enable LNA Automatic Gain Control
    int hydrasdr_set_lna_agc(hydrasdr_device* device, uint8_t value)
    
    # Parameter value:
    # 0=Disable MIXER Automatic Gain Control
    # 1=Enable MIXER Automatic Gain Control
    int hydrasdr_set_mixer_agc(hydrasdr_device* device, uint8_t value)
    
    # Parameter value: 0..21
    int hydrasdr_set_linearity_gain(hydrasdr_device* device, uint8_t value)
    
    # Parameter value: 0..21
    int hydrasdr_set_sensitivity_gain(hydrasdr_device* device, uint8_t value)
    
    # Parameter value shall be 0=Disable BiasT or 1=Enable BiasT
    int hydrasdr_set_rf_bias(hydrasdr_device* dev, uint8_t value)
    
    # Parameter value shall be 0=Disable Packing or 1=Enable Packing
    int hydrasdr_set_packing(hydrasdr_device* device, uint8_t value)
    
    const char* hydrasdr_error_name(hydrasdr_error errcode)
    const char* hydrasdr_board_id_name(hydrasdr_board_id board_id)
    
    # Parameter sector_num shall be between 2 & 13 (sector 0 & 1 are reserved)
    int hydrasdr_spiflash_erase_sector(hydrasdr_device* device, const uint16_t sector_num)
