/*
Copyright (c) 2012, Jared Boone <jared@sharebrained.com>
Copyright (c) 2013, Michael Ossmann <mike@ossmann.com>
Copyright (c) 2013-2016, Benjamin Vernoux <bvernoux@airspy.com>
Copyright (C) 2013-2016, Youssef Touil <youssef@airspy.com>

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

		Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
		Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the 
	documentation and/or other materials provided with the distribution.
		Neither the name of AirSpy nor the names of its contributors may be used to endorse or promote products derived from this software
	without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef __AIRSPY_H__
#define __AIRSPY_H__

#include <stdint.h>
#include "airspy_commands.h"

#define AIRSPY_VERSION "1.0.9"
#define AIRSPY_VER_MAJOR 1
#define AIRSPY_VER_MINOR 0
#define AIRSPY_VER_REVISION 9

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

#ifdef __cplusplus
extern "C"
{
#endif

enum airspy_error
{
	AIRSPY_SUCCESS = 0,
	AIRSPY_TRUE = 1,
	AIRSPY_ERROR_INVALID_PARAM = -2,
	AIRSPY_ERROR_NOT_FOUND = -5,
	AIRSPY_ERROR_BUSY = -6,
	AIRSPY_ERROR_NO_MEM = -11,
	AIRSPY_ERROR_LIBUSB = -1000,
	AIRSPY_ERROR_THREAD = -1001,
	AIRSPY_ERROR_STREAMING_THREAD_ERR = -1002,
	AIRSPY_ERROR_STREAMING_STOPPED = -1003,
	AIRSPY_ERROR_OTHER = -9999,
};

enum airspy_board_id
{
	AIRSPY_BOARD_ID_PROTO_AIRSPY  = 0,
	AIRSPY_BOARD_ID_INVALID = 0xFF,
};

enum airspy_sample_type
{
	AIRSPY_SAMPLE_FLOAT32_IQ = 0,   /* 2 * 32bit float per sample */
	AIRSPY_SAMPLE_FLOAT32_REAL = 1, /* 1 * 32bit float per sample */
	AIRSPY_SAMPLE_INT16_IQ = 2,     /* 2 * 16bit int per sample */
	AIRSPY_SAMPLE_INT16_REAL = 3,   /* 1 * 16bit int per sample */
	AIRSPY_SAMPLE_UINT16_REAL = 4,  /* 1 * 16bit unsigned int per sample */
	AIRSPY_SAMPLE_RAW = 5,          /* Raw packed samples from the device */
	AIRSPY_SAMPLE_END = 6           /* Number of supported sample types */
};

#define MAX_CONFIG_PAGE_SIZE (0x10000)

struct airspy_device;

typedef struct {
	struct airspy_device* device;
	void* ctx;
	void* samples;
	int sample_count;
	uint64_t dropped_samples;
	enum airspy_sample_type sample_type;
} airspy_transfer_t, airspy_transfer;

typedef struct {
	uint32_t part_id[2];
	uint32_t serial_no[4];
} airspy_read_partid_serialno_t;

typedef struct {
	uint32_t major_version;
	uint32_t minor_version;
	uint32_t revision;
} airspy_lib_version_t;

typedef int (*airspy_sample_block_cb_fn)(airspy_transfer* transfer);

extern ADDAPI void ADDCALL airspy_lib_version(airspy_lib_version_t* lib_version);
/* airspy_init() deprecated */
extern ADDAPI int ADDCALL airspy_init(void);
/* airspy_exit() deprecated */
extern ADDAPI int ADDCALL airspy_exit(void);
 
extern ADDAPI int ADDCALL airspy_open_sn(struct airspy_device** device, uint64_t serial_number);
extern ADDAPI int ADDCALL airspy_open(struct airspy_device** device);
extern ADDAPI int ADDCALL airspy_close(struct airspy_device* device);

extern ADDAPI int ADDCALL airspy_get_samplerates(struct airspy_device* device, uint32_t* buffer, const uint32_t len);

/* Parameter samplerate can be either the index of a samplerate or directly its value in Hz within the list returned by airspy_get_samplerates() */
extern ADDAPI int ADDCALL airspy_set_samplerate(struct airspy_device* device, uint32_t samplerate);

extern ADDAPI int ADDCALL airspy_set_conversion_filter_float32(struct airspy_device* device, const float *kernel, const uint32_t len);
extern ADDAPI int ADDCALL airspy_set_conversion_filter_int16(struct airspy_device* device, const int16_t *kernel, const uint32_t len);

extern ADDAPI int ADDCALL airspy_start_rx(struct airspy_device* device, airspy_sample_block_cb_fn callback, void* rx_ctx);
extern ADDAPI int ADDCALL airspy_stop_rx(struct airspy_device* device);

/* return AIRSPY_TRUE if success */
extern ADDAPI int ADDCALL airspy_is_streaming(struct airspy_device* device);

extern ADDAPI int ADDCALL airspy_si5351c_write(struct airspy_device* device, uint8_t register_number, uint8_t value);
extern ADDAPI int ADDCALL airspy_si5351c_read(struct airspy_device* device, uint8_t register_number, uint8_t* value);

extern ADDAPI int ADDCALL airspy_config_write(struct airspy_device* device, const uint8_t page_index, const uint16_t length, unsigned char *data);
extern ADDAPI int ADDCALL airspy_config_read(struct airspy_device* device, const uint8_t page_index, const uint16_t length, unsigned char *data);

extern ADDAPI int ADDCALL airspy_r820t_write(struct airspy_device* device, uint8_t register_number, uint8_t value);
extern ADDAPI int ADDCALL airspy_r820t_read(struct airspy_device* device, uint8_t register_number, uint8_t* value);

/* Parameter value shall be 0=clear GPIO or 1=set GPIO */
extern ADDAPI int ADDCALL airspy_gpio_write(struct airspy_device* device, airspy_gpio_port_t port, airspy_gpio_pin_t pin, uint8_t value);
/* Parameter value corresponds to GPIO state 0 or 1 */
extern ADDAPI int ADDCALL airspy_gpio_read(struct airspy_device* device, airspy_gpio_port_t port, airspy_gpio_pin_t pin, uint8_t* value);

/* Parameter value shall be 0=GPIO Input direction or 1=GPIO Output direction */
extern ADDAPI int ADDCALL airspy_gpiodir_write(struct airspy_device* device, airspy_gpio_port_t port, airspy_gpio_pin_t pin, uint8_t value);
extern ADDAPI int ADDCALL airspy_gpiodir_read(struct airspy_device* device, airspy_gpio_port_t port, airspy_gpio_pin_t pin, uint8_t* value);

extern ADDAPI int ADDCALL airspy_spiflash_erase(struct airspy_device* device);
extern ADDAPI int ADDCALL airspy_spiflash_write(struct airspy_device* device, const uint32_t address, const uint16_t length, unsigned char* const data);
extern ADDAPI int ADDCALL airspy_spiflash_read(struct airspy_device* device, const uint32_t address, const uint16_t length, unsigned char* data);

extern ADDAPI int ADDCALL airspy_board_id_read(struct airspy_device* device, uint8_t* value);
/* Parameter length shall be at least 128bytes */
extern ADDAPI int ADDCALL airspy_version_string_read(struct airspy_device* device, char* version, uint8_t length);

extern ADDAPI int ADDCALL airspy_board_partid_serialno_read(struct airspy_device* device, airspy_read_partid_serialno_t* read_partid_serialno);

extern ADDAPI int ADDCALL airspy_set_sample_type(struct airspy_device* device, enum airspy_sample_type sample_type);

/* Parameter freq_hz shall be between 24000000(24MHz) and 1750000000(1.75GHz) */
extern ADDAPI int ADDCALL airspy_set_freq(struct airspy_device* device, const uint32_t freq_hz);

/* Parameter value shall be between 0 and 15 */
extern ADDAPI int ADDCALL airspy_set_lna_gain(struct airspy_device* device, uint8_t value);

/* Parameter value shall be between 0 and 15 */
extern ADDAPI int ADDCALL airspy_set_mixer_gain(struct airspy_device* device, uint8_t value);

/* Parameter value shall be between 0 and 15 */
extern ADDAPI int ADDCALL airspy_set_vga_gain(struct airspy_device* device, uint8_t value);

/* Parameter value:
	0=Disable LNA Automatic Gain Control
	1=Enable LNA Automatic Gain Control
*/
extern ADDAPI int ADDCALL airspy_set_lna_agc(struct airspy_device* device, uint8_t value);
/* Parameter value:
	0=Disable MIXER Automatic Gain Control
	1=Enable MIXER Automatic Gain Control
*/
extern ADDAPI int ADDCALL airspy_set_mixer_agc(struct airspy_device* device, uint8_t value);

/* Parameter value: 0..21 */
extern ADDAPI int ADDCALL airspy_set_linearity_gain(struct airspy_device* device, uint8_t value);

/* Parameter value: 0..21 */
extern ADDAPI int ADDCALL airspy_set_sensitivity_gain(struct airspy_device* device, uint8_t value);

/* Parameter value shall be 0=Disable BiasT or 1=Enable BiasT */
extern ADDAPI int ADDCALL airspy_set_rf_bias(struct airspy_device* dev, uint8_t value);

/* Parameter value shall be 0=Disable Packing or 1=Enable Packing */
extern ADDAPI int ADDCALL airspy_set_packing(struct airspy_device* device, uint8_t value);

extern ADDAPI const char* ADDCALL airspy_error_name(enum airspy_error errcode);
extern ADDAPI const char* ADDCALL airspy_board_id_name(enum airspy_board_id board_id);

/* Parameter sector_num shall be between 2 & 13 (sector 0 & 1 are reserved) */
extern ADDAPI int ADDCALL airspy_spiflash_erase_sector(struct airspy_device* device, const uint16_t sector_num);

#ifdef __cplusplus
} // __cplusplus defined.
#endif

#endif//__AIRSPY_H__
