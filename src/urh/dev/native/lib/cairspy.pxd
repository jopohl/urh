ctypedef unsigned char uint8_t
ctypedef short int16_t
ctypedef unsigned short uint16_t
ctypedef unsigned int uint32_t
ctypedef unsigned long long uint64_t

cdef extern from "libairspy/airspy.h":
    enum airspy_error:
        AIRSPY_SUCCESS = 0
        AIRSPY_TRUE = 1
        AIRSPY_ERROR_INVALID_PARAM = -2
        AIRSPY_ERROR_NOT_FOUND = -5
        AIRSPY_ERROR_BUSY = -6
        AIRSPY_ERROR_NO_MEM = -11
        AIRSPY_ERROR_LIBUSB = -1000
        AIRSPY_ERROR_THREAD = -1001
        AIRSPY_ERROR_STREAMING_THREAD_ERR = -1002
        AIRSPY_ERROR_STREAMING_STOPPED = -1003
        AIRSPY_ERROR_OTHER = -9999

    enum airspy_board_id:
        AIRSPY_BOARD_ID_PROTO_AIRSPY = 0
        AIRSPY_BOARD_ID_INVALID = 0xFF

    enum airspy_sample_type:
        AIRSPY_SAMPLE_FLOAT32_IQ = 0    # 2 * 32bit float per sample
        AIRSPY_SAMPLE_FLOAT32_REAL = 1  # 1 * 32bit float per sample
        AIRSPY_SAMPLE_INT16_IQ = 2      # 2 * 16bit int per sample
        AIRSPY_SAMPLE_INT16_REAL = 3    # 1 * 16bit int per sample
        AIRSPY_SAMPLE_UINT16_REAL = 4   # 1 * 16bit unsigned int per sample
        AIRSPY_SAMPLE_RAW = 5           # Raw packed samples from the device
        AIRSPY_SAMPLE_END = 6           # Number of supported sample types

    struct airspy_device

    ctypedef struct airspy_transfer:
        airspy_device* device
        void* ctx
        void* samples
        int sample_count
        uint64_t dropped_samples
        airspy_sample_type sample_type

    ctypedef struct airspy_read_partid_serialno_t:
        uint32_t part_id[2]
        uint32_t serial_no[4]

    ctypedef struct airspy_lib_version_t:
        uint32_t major_version
        uint32_t minor_version
        uint32_t revision

    ctypedef int (*airspy_sample_block_cb_fn)(airspy_transfer* transfer)
    
    void airspy_lib_version(airspy_lib_version_t* lib_version)
    int airspy_open_sn(airspy_device** device, uint64_t serial_number)
    int airspy_open(airspy_device** device)
    int airspy_close(airspy_device* device)
    
    int airspy_get_samplerates(airspy_device* device, uint32_t* buffer, const uint32_t len)
    
    # Parameter samplerate can be either the index of a samplerate or directly its value in Hz within the list returned by airspy_get_samplerates()
    int airspy_set_samplerate(airspy_device* device, uint32_t samplerate)
    
    int airspy_set_conversion_filter_float32(airspy_device* device, const float *kernel, const uint32_t len)
    int airspy_set_conversion_filter_int16(airspy_device* device, const int16_t *kernel, const uint32_t len)
    
    int airspy_start_rx(airspy_device* device, airspy_sample_block_cb_fn callback, void* rx_ctx)
    int airspy_stop_rx(airspy_device* device)
    
    # return AIRSPY_TRUE if success
    int airspy_is_streaming(airspy_device* device)
    
    int airspy_si5351c_write(airspy_device* device, uint8_t register_number, uint8_t value)
    int airspy_si5351c_read(airspy_device* device, uint8_t register_number, uint8_t* value)
    
    int airspy_config_write(airspy_device* device, const uint8_t page_index, const uint16_t length, unsigned char *data)
    int airspy_config_read(airspy_device* device, const uint8_t page_index, const uint16_t length, unsigned char *data)
    
    int airspy_r820t_write(airspy_device* device, uint8_t register_number, uint8_t value)
    int airspy_r820t_read(airspy_device* device, uint8_t register_number, uint8_t* value)
    
    int airspy_board_id_read(airspy_device* device, uint8_t* value)
    # Parameter length shall be at least 128bytes
    int airspy_version_string_read(airspy_device* device, char* version, uint8_t length)
    
    int airspy_board_partid_serialno_read(airspy_device* device, airspy_read_partid_serialno_t* read_partid_serialno)
    
    int airspy_set_sample_type(airspy_device* device, airspy_sample_type sample_type)
    
    # Parameter freq_hz shall be between 24000000(24MHz) and 1750000000(1.75GHz)
    int airspy_set_freq(airspy_device* device, const uint32_t freq_hz)
    
    # Parameter value shall be between 0 and 15
    int airspy_set_lna_gain(airspy_device* device, uint8_t value)
    
    # Parameter value shall be between 0 and 15
    int airspy_set_mixer_gain(airspy_device* device, uint8_t value)
    
    # Parameter value shall be between 0 and 15
    int airspy_set_vga_gain(airspy_device* device, uint8_t value)
    
    # Parameter value:
    # 0=Disable LNA Automatic Gain Control
    # 1=Enable LNA Automatic Gain Control
    int airspy_set_lna_agc(airspy_device* device, uint8_t value)
    
    # Parameter value:
    # 0=Disable MIXER Automatic Gain Control
    # 1=Enable MIXER Automatic Gain Control
    int airspy_set_mixer_agc(airspy_device* device, uint8_t value)
    
    # Parameter value: 0..21
    int airspy_set_linearity_gain(airspy_device* device, uint8_t value)
    
    # Parameter value: 0..21
    int airspy_set_sensitivity_gain(airspy_device* device, uint8_t value)
    
    # Parameter value shall be 0=Disable BiasT or 1=Enable BiasT
    int airspy_set_rf_bias(airspy_device* dev, uint8_t value)
    
    # Parameter value shall be 0=Disable Packing or 1=Enable Packing
    int airspy_set_packing(airspy_device* device, uint8_t value)
    
    const char* airspy_error_name(airspy_error errcode)
    const char* airspy_board_id_name(airspy_board_id board_id)
    
    # Parameter sector_num shall be between 2 & 13 (sector 0 & 1 are reserved)
    int airspy_spiflash_erase_sector(airspy_device* device, const uint16_t sector_num)
