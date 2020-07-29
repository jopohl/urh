from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t

cdef extern from "libhackrf/hackrf.h":
    enum hackrf_error:
        HACKRF_SUCCESS = 0
        HACKRF_TRUE = 1
        HACKRF_ERROR_INVALID_PARAM = -2
        HACKRF_ERROR_NOT_FOUND = -5
        HACKRF_ERROR_BUSY = -6
        HACKRF_ERROR_NO_MEM = -11
        HACKRF_ERROR_LIBUSB = -1000
        HACKRF_ERROR_THREAD = -1001
        HACKRF_ERROR_STREAMING_THREAD_ERR = -1002
        HACKRF_ERROR_STREAMING_STOPPED = -1003
        HACKRF_ERROR_STREAMING_EXIT_CALLED = -1004
        HACKRF_ERROR_OTHER = -9999

    enum hackrf_board_id:
        BOARD_ID_JELLYBEAN = 0
        BOARD_ID_JAWBREAKER = 1
        BOARD_ID_HACKRF_ONE = 2
        BOARD_ID_INVALID = 0xFF

    enum hackrf_usb_board_id:
        USB_BOARD_ID_JAWBREAKER = 0x604B
        USB_BOARD_ID_HACKRF_ONE = 0x6089
        USB_BOARD_ID_RAD1O = 0xCC15
        USB_BOARD_ID_INVALID = 0xFFFF

    enum rf_path_filter:
        RF_PATH_FILTER_BYPASS = 0
        RF_PATH_FILTER_LOW_PASS = 1
        RF_PATH_FILTER_HIGH_PASS = 2

    ctypedef enum transceiver_mode_t:
        TRANSCEIVER_MODE_OFF = 0
        TRANSCEIVER_MODE_RX = 1
        TRANSCEIVER_MODE_TX = 2
        TRANSCEIVER_MODE_SS = 3
        TRANSCEIVER_MODE_CPLD_UPDATE = 4

    ctypedef struct hackrf_device:
        pass

    ctypedef struct hackrf_transfer:
        hackrf_device* device
        uint8_t* buffer
        int buffer_length
        int valid_length
        void* rx_ctx
        void* tx_ctx

    ctypedef struct read_partid_serialno_t:
        uint32_t part_id[2]
        uint32_t serial_no[4]

    ctypedef struct hackrf_device_list:
        char ** serial_numbers
        hackrf_usb_board_id * usb_board_ids
        int *usb_device_index
        int devicecount

        void ** usb_devices
        int usb_devicecount

    ctypedef hackrf_device_list hackrf_device_list_t;

    ctypedef int (*hackrf_sample_block_cb_fn)(hackrf_transfer* transfer)

    
    int hackrf_init()
    int hackrf_exit()
    

    int hackrf_device_list_open(hackrf_device_list_t *list, int idx, hackrf_device** device)
    void hackrf_device_list_free(hackrf_device_list_t *list)
     
    int hackrf_open(hackrf_device** device);

    IF HACKRF_MULTI_DEVICE_SUPPORT == 1:
        int hackrf_open_by_serial(const char* desired_serial_number, hackrf_device** device)
        hackrf_device_list_t* hackrf_device_list()


    int hackrf_close(hackrf_device* device)
     
    int hackrf_start_rx(hackrf_device* device, hackrf_sample_block_cb_fn callback, void* rx_ctx)
    int hackrf_stop_rx(hackrf_device* device)
     
    int hackrf_start_tx(hackrf_device* device, hackrf_sample_block_cb_fn callback, void* tx_ctx)
    int hackrf_stop_tx(hackrf_device* device)
    
    # return HACKRF_TRUE if success
    int hackrf_is_streaming(hackrf_device* device)
     
    int hackrf_max2837_read(hackrf_device* device, uint8_t register_number, uint16_t* value)
    int hackrf_max2837_write(hackrf_device* device, uint8_t register_number, uint16_t value)
     
    int hackrf_si5351c_read(hackrf_device* device, uint16_t register_number, uint16_t* value)
    int hackrf_si5351c_write(hackrf_device* device, uint16_t register_number, uint16_t value)
     
    int hackrf_set_baseband_filter_bandwidth(hackrf_device* device, const uint32_t bandwidth_hz)
     
    int hackrf_rffc5071_read(hackrf_device* device, uint8_t register_number, uint16_t* value)
    int hackrf_rffc5071_write(hackrf_device* device, uint8_t register_number, uint16_t value)
     
    int hackrf_spiflash_erase(hackrf_device* device)
    int hackrf_spiflash_write(hackrf_device* device, const uint32_t address, const uint16_t length, const unsigned char* data)
    int hackrf_spiflash_read(hackrf_device* device, const uint32_t address, const uint16_t length, unsigned char* data)
    
    # device will need to be reset after hackrf_cpld_write
    int hackrf_cpld_write(hackrf_device* device, const unsigned char* data, const unsigned int total_length)
            
    int hackrf_board_id_read(hackrf_device* device, uint8_t* value)
    int hackrf_version_string_read(hackrf_device* device, char* version, uint8_t length)
    
    int hackrf_set_freq(hackrf_device* device, const uint64_t freq_hz)
    # extern  int  hackrf_set_freq_explicit(hackrf_device* device,
    #         const uint64_t if_freq_hz, const uint64_t lo_freq_hz,
    #         const enum rf_path_filter path)
    
    # currently 8-20Mhz - either as a fraction, i.e. freq 20000000hz divider 2 -> 10Mhz or as plain old 10000000hz (double)
    #    preferred rates are 8, 10, 12.5, 16, 20Mhz due to less jitter
    int hackrf_set_sample_rate_manual(hackrf_device* device, const uint32_t freq_hz, const uint32_t divider)
    int hackrf_set_sample_rate(hackrf_device* device, const double freq_hz)
    
    # external amp, bool on/off
    int hackrf_set_amp_enable(hackrf_device* device, const uint8_t value)

    # Bias Tee, bool on/off
    int hackrf_set_antenna_enable(hackrf_device* device, const uint8_t value)

    int hackrf_board_partid_serialno_read(hackrf_device* device, read_partid_serialno_t* read_partid_serialno)
    
    # range 0-40 step 8d, IF gain in osmosdr
    int hackrf_set_lna_gain(hackrf_device* device, uint32_t value)
    
    # range 0-62 step 2db, BB gain in osmosdr
    int hackrf_set_vga_gain(hackrf_device* device, uint32_t value)
    
    # range 0-47 step 1db
    int hackrf_set_txvga_gain(hackrf_device* device, uint32_t value)
    
    const char* hackrf_error_name(hackrf_error errcode)
    const char* hackrf_board_id_name(hackrf_board_id board_id)
    const char* hackrf_usb_board_id_name(hackrf_usb_board_id usb_board_id)
    const char* hackrf_filter_path_name(const rf_path_filter path)
    
    # Compute nearest freq for bw filter (manual filter)
    uint32_t hackrf_compute_baseband_filter_bw_round_down_lt(const uint32_t bandwidth_hz);
    # Compute best default value depending on sample rate (auto filter)
    uint32_t hackrf_compute_baseband_filter_bw(const uint32_t bandwidth_hz);
