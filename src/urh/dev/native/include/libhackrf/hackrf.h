/*
Copyright (c) 2012, Jared Boone <jared@sharebrained.com>
Copyright (c) 2013, Benjamin Vernoux <titanmkd@gmail.com>
Copyright (c) 2013, Michael Ossmann <mike@ossmann.com>

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the 
	documentation and/or other materials provided with the distribution.
    Neither the name of Great Scott Gadgets nor the names of its contributors may be used to endorse or promote products derived from this software
	without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef __HACKRF_H__
#define __HACKRF_H__

#include <stdint.h>

#ifdef _WIN32
   #define ADD_EXPORTS
   
  /* You should define ADD_EXPORTS *only* when building the DLL. */
  #ifdef ADD_EXPORTS
    #define ADDAPI __declspec(dllexport)
  #else
    #define ADDAPI __declspec(dllimport)
  #endif

  /* Define calling convention in one place, for convenience. */
  #define ADDCALL __cdecl

#else /* _WIN32 not defined. */

  /* Define with no value on non-Windows OSes. */
  #define ADDAPI
  #define ADDCALL

#endif

#define SAMPLES_PER_BLOCK 16384
#define MAX_SWEEP_RANGES 10

enum hackrf_error {
	HACKRF_SUCCESS = 0,
	HACKRF_TRUE = 1,
	HACKRF_ERROR_INVALID_PARAM = -2,
	HACKRF_ERROR_NOT_FOUND = -5,
	HACKRF_ERROR_BUSY = -6,
	HACKRF_ERROR_NO_MEM = -11,
	HACKRF_ERROR_LIBUSB = -1000,
	HACKRF_ERROR_THREAD = -1001,
	HACKRF_ERROR_STREAMING_THREAD_ERR = -1002,
	HACKRF_ERROR_STREAMING_STOPPED = -1003,
	HACKRF_ERROR_STREAMING_EXIT_CALLED = -1004,
	HACKRF_ERROR_USB_API_VERSION = -1005,
	HACKRF_ERROR_OTHER = -9999,
};

enum hackrf_board_id {
	BOARD_ID_JELLYBEAN  = 0,
	BOARD_ID_JAWBREAKER = 1,
	BOARD_ID_HACKRF_ONE = 2,
	BOARD_ID_RAD1O = 3,
	BOARD_ID_INVALID = 0xFF,
};

enum hackrf_usb_board_id {
	USB_BOARD_ID_JAWBREAKER = 0x604B,
	USB_BOARD_ID_HACKRF_ONE = 0x6089,
	USB_BOARD_ID_RAD1O = 0xCC15,
	USB_BOARD_ID_INVALID = 0xFFFF,
};

enum rf_path_filter {
	RF_PATH_FILTER_BYPASS = 0,
	RF_PATH_FILTER_LOW_PASS = 1,
	RF_PATH_FILTER_HIGH_PASS = 2,
};

enum operacake_ports {
	OPERACAKE_PA1 = 0,
	OPERACAKE_PA2 = 1,
	OPERACAKE_PA3 = 2,
	OPERACAKE_PA4 = 3,
	OPERACAKE_PB1 = 4,
	OPERACAKE_PB2 = 5,
	OPERACAKE_PB3 = 6,
	OPERACAKE_PB4 = 7,
};

enum sweep_style {
	LINEAR = 0,
	INTERLEAVED = 1,
};

typedef struct hackrf_device hackrf_device;

typedef struct {
	hackrf_device* device;
	uint8_t* buffer;
	int buffer_length;
	int valid_length;
	void* rx_ctx;
	void* tx_ctx;
} hackrf_transfer;

typedef struct {
	uint32_t part_id[2];
	uint32_t serial_no[4];
} read_partid_serialno_t;


struct hackrf_device_list {
	char **serial_numbers;
	enum hackrf_usb_board_id *usb_board_ids;
	int *usb_device_index;
	int devicecount;
	
	void **usb_devices;
	int usb_devicecount;
};
typedef struct hackrf_device_list hackrf_device_list_t;

typedef int (*hackrf_sample_block_cb_fn)(hackrf_transfer* transfer);

#ifdef __cplusplus
extern "C"
{
#endif

extern ADDAPI int ADDCALL hackrf_init();
extern ADDAPI int ADDCALL hackrf_exit();

extern ADDAPI const char* ADDCALL hackrf_library_version();
extern ADDAPI const char* ADDCALL hackrf_library_release();

extern ADDAPI hackrf_device_list_t* ADDCALL hackrf_device_list();
extern ADDAPI int ADDCALL hackrf_device_list_open(hackrf_device_list_t *list, int idx, hackrf_device** device);
extern ADDAPI void ADDCALL hackrf_device_list_free(hackrf_device_list_t *list);
 
extern ADDAPI int ADDCALL hackrf_open(hackrf_device** device);
extern ADDAPI int ADDCALL hackrf_open_by_serial(const char* const desired_serial_number, hackrf_device** device);
extern ADDAPI int ADDCALL hackrf_close(hackrf_device* device);
 
extern ADDAPI int ADDCALL hackrf_start_rx(hackrf_device* device, hackrf_sample_block_cb_fn callback, void* rx_ctx);
extern ADDAPI int ADDCALL hackrf_stop_rx(hackrf_device* device);
 
extern ADDAPI int ADDCALL hackrf_start_tx(hackrf_device* device, hackrf_sample_block_cb_fn callback, void* tx_ctx);
extern ADDAPI int ADDCALL hackrf_stop_tx(hackrf_device* device);

/* return HACKRF_TRUE if success */
extern ADDAPI int ADDCALL hackrf_is_streaming(hackrf_device* device);
 
extern ADDAPI int ADDCALL hackrf_max2837_read(hackrf_device* device, uint8_t register_number, uint16_t* value);
extern ADDAPI int ADDCALL hackrf_max2837_write(hackrf_device* device, uint8_t register_number, uint16_t value);
 
extern ADDAPI int ADDCALL hackrf_si5351c_read(hackrf_device* device, uint16_t register_number, uint16_t* value);
extern ADDAPI int ADDCALL hackrf_si5351c_write(hackrf_device* device, uint16_t register_number, uint16_t value);
 
extern ADDAPI int ADDCALL hackrf_set_baseband_filter_bandwidth(hackrf_device* device, const uint32_t bandwidth_hz);
 
extern ADDAPI int ADDCALL hackrf_rffc5071_read(hackrf_device* device, uint8_t register_number, uint16_t* value);
extern ADDAPI int ADDCALL hackrf_rffc5071_write(hackrf_device* device, uint8_t register_number, uint16_t value);
 
extern ADDAPI int ADDCALL hackrf_spiflash_erase(hackrf_device* device);
extern ADDAPI int ADDCALL hackrf_spiflash_write(hackrf_device* device, const uint32_t address, const uint16_t length, unsigned char* const data);
extern ADDAPI int ADDCALL hackrf_spiflash_read(hackrf_device* device, const uint32_t address, const uint16_t length, unsigned char* data);

/* device will need to be reset after hackrf_cpld_write */
extern ADDAPI int ADDCALL hackrf_cpld_write(hackrf_device* device,
		unsigned char* const data, const unsigned int total_length);
		
extern ADDAPI int ADDCALL hackrf_board_id_read(hackrf_device* device, uint8_t* value);
extern ADDAPI int ADDCALL hackrf_version_string_read(hackrf_device* device, char* version, uint8_t length);
extern ADDAPI int ADDCALL hackrf_usb_api_version_read(hackrf_device* device, uint16_t* version);

extern ADDAPI int ADDCALL hackrf_set_freq(hackrf_device* device, const uint64_t freq_hz);
extern ADDAPI int ADDCALL hackrf_set_freq_explicit(hackrf_device* device,
		const uint64_t if_freq_hz, const uint64_t lo_freq_hz,
		const enum rf_path_filter path);

/* currently 8-20Mhz - either as a fraction, i.e. freq 20000000hz divider 2 -> 10Mhz or as plain old 10000000hz (double)
	preferred rates are 8, 10, 12.5, 16, 20Mhz due to less jitter */
extern ADDAPI int ADDCALL hackrf_set_sample_rate_manual(hackrf_device* device, const uint32_t freq_hz, const uint32_t divider);
extern ADDAPI int ADDCALL hackrf_set_sample_rate(hackrf_device* device, const double freq_hz);

/* external amp, bool on/off */
extern ADDAPI int ADDCALL hackrf_set_amp_enable(hackrf_device* device, const uint8_t value);

extern ADDAPI int ADDCALL hackrf_board_partid_serialno_read(hackrf_device* device, read_partid_serialno_t* read_partid_serialno);

/* range 0-40 step 8d, IF gain in osmosdr  */
extern ADDAPI int ADDCALL hackrf_set_lna_gain(hackrf_device* device, uint32_t value);

/* range 0-62 step 2db, BB gain in osmosdr */
extern ADDAPI int ADDCALL hackrf_set_vga_gain(hackrf_device* device, uint32_t value);

/* range 0-47 step 1db */
extern ADDAPI int ADDCALL hackrf_set_txvga_gain(hackrf_device* device, uint32_t value);

/* antenna port power control */
extern ADDAPI int ADDCALL hackrf_set_antenna_enable(hackrf_device* device, const uint8_t value);

extern ADDAPI const char* ADDCALL hackrf_error_name(enum hackrf_error errcode);
extern ADDAPI const char* ADDCALL hackrf_board_id_name(enum hackrf_board_id board_id);
extern ADDAPI const char* ADDCALL hackrf_usb_board_id_name(enum hackrf_usb_board_id usb_board_id);
extern ADDAPI const char* ADDCALL hackrf_filter_path_name(const enum rf_path_filter path);

/* Compute nearest freq for bw filter (manual filter) */
extern ADDAPI uint32_t ADDCALL hackrf_compute_baseband_filter_bw_round_down_lt(const uint32_t bandwidth_hz);
/* Compute best default value depending on sample rate (auto filter) */
extern ADDAPI uint32_t ADDCALL hackrf_compute_baseband_filter_bw(const uint32_t bandwidth_hz);

/* All features below require USB API version 0x1002 or higher) */

/* set hardware sync mode  */
extern ADDAPI int ADDCALL hackrf_set_hw_sync_mode(hackrf_device* device, const uint8_t value);

/* Start sweep mode */
extern ADDAPI int ADDCALL hackrf_init_sweep(hackrf_device* device,
		const uint16_t* frequency_list, const int num_ranges,
		const uint32_t num_samples, const uint32_t step_width,
		const uint32_t offset, const enum sweep_style style);

/* Operacake functions */
extern ADDAPI int ADDCALL hackrf_get_operacake_boards(hackrf_device* device, uint8_t* boards);
extern ADDAPI int ADDCALL hackrf_set_operacake_ports(hackrf_device* device,
                                       uint8_t address,
                                       uint8_t port_a,
                                       uint8_t port_b);

extern ADDAPI int ADDCALL hackrf_reset(hackrf_device* device);

#ifdef __cplusplus
} // __cplusplus defined.
#endif

#endif /*__HACKRF_H__*/
