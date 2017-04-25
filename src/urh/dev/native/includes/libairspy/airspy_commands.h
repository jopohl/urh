/*
Copyright (c) 2013-2016, Benjamin Vernoux <bvernoux@airspy.com>

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

#ifndef __AIRSPY_COMMANDS_H__
#define __AIRSPY_COMMANDS_H__

#include <stdint.h>

#ifdef __cplusplus
extern "C"
{
#endif

typedef enum
{
    RECEIVER_MODE_OFF = 0,
    RECEIVER_MODE_RX = 1
} receiver_mode_t;

/*
  Note: airspy_samplerate_t is now obsolete and left for backward compatibility.
  The list of supported sample rates should be retrieved at run time by calling airspy_get_samplerates().
  Refer to the Airspy Tools for illustrations.
*/
typedef enum 
{
    AIRSPY_SAMPLERATE_10MSPS = 0, /* 12bits 10MHz IQ */
    AIRSPY_SAMPLERATE_2_5MSPS = 1, /* 12bits 2.5MHz IQ */
    AIRSPY_SAMPLERATE_END = 2 /* End index for sample rate (corresponds to number of samplerate) */
} airspy_samplerate_t;


#define AIRSPY_CONF_CMD_SHIFT_BIT (3) // Up to 3bits=8 samplerates (airspy_samplerate_t enum shall not exceed 7)

// Commands (usb vendor request) shared between Firmware and Host.
#define AIRSPY_CMD_MAX (27)
typedef enum
{
    AIRSPY_INVALID                    = 0 ,
    AIRSPY_RECEIVER_MODE              = 1 ,
    AIRSPY_SI5351C_WRITE              = 2 ,
    AIRSPY_SI5351C_READ               = 3 ,
    AIRSPY_R820T_WRITE                = 4 ,
    AIRSPY_R820T_READ                 = 5 ,
    AIRSPY_SPIFLASH_ERASE             = 6 ,
    AIRSPY_SPIFLASH_WRITE             = 7 ,
    AIRSPY_SPIFLASH_READ              = 8 ,
    AIRSPY_BOARD_ID_READ              = 9 ,
    AIRSPY_VERSION_STRING_READ        = 10,
    AIRSPY_BOARD_PARTID_SERIALNO_READ = 11,
    AIRSPY_SET_SAMPLERATE             = 12,
    AIRSPY_SET_FREQ                   = 13,
    AIRSPY_SET_LNA_GAIN               = 14,
    AIRSPY_SET_MIXER_GAIN             = 15,
    AIRSPY_SET_VGA_GAIN               = 16,
    AIRSPY_SET_LNA_AGC                = 17,
    AIRSPY_SET_MIXER_AGC              = 18,
    AIRSPY_MS_VENDOR_CMD              = 19,
    AIRSPY_SET_RF_BIAS_CMD            = 20,
    AIRSPY_GPIO_WRITE                 = 21,
    AIRSPY_GPIO_READ                  = 22,
    AIRSPY_GPIODIR_WRITE              = 23,
    AIRSPY_GPIODIR_READ               = 24,
    AIRSPY_GET_SAMPLERATES            = 25,
    AIRSPY_SET_PACKING                = 26,
    AIRSPY_SPIFLASH_ERASE_SECTOR      = AIRSPY_CMD_MAX
} airspy_vendor_request;

typedef enum
{
    CONFIG_CALIBRATION = 0,
    //CONFIG_META        = 1,
} airspy_common_config_pages_t;

typedef enum
{
    GPIO_PORT0 = 0,
    GPIO_PORT1 = 1,
    GPIO_PORT2 = 2,
    GPIO_PORT3 = 3,
    GPIO_PORT4 = 4,
    GPIO_PORT5 = 5,
    GPIO_PORT6 = 6,
    GPIO_PORT7 = 7
} airspy_gpio_port_t;

typedef enum
{
    GPIO_PIN0 = 0,
    GPIO_PIN1 = 1,
    GPIO_PIN2 = 2,
    GPIO_PIN3 = 3,
    GPIO_PIN4 = 4,
    GPIO_PIN5 = 5,
    GPIO_PIN6 = 6,
    GPIO_PIN7 = 7,
    GPIO_PIN8 = 8,
    GPIO_PIN9 = 9,
    GPIO_PIN10 = 10,
    GPIO_PIN11 = 11,
    GPIO_PIN12 = 12,
    GPIO_PIN13 = 13,
    GPIO_PIN14 = 14,
    GPIO_PIN15 = 15,
    GPIO_PIN16 = 16,
    GPIO_PIN17 = 17,
    GPIO_PIN18 = 18,
    GPIO_PIN19 = 19,
    GPIO_PIN20 = 20,
    GPIO_PIN21 = 21,
    GPIO_PIN22 = 22,
    GPIO_PIN23 = 23,
    GPIO_PIN24 = 24,
    GPIO_PIN25 = 25,
    GPIO_PIN26 = 26,
    GPIO_PIN27 = 27,
    GPIO_PIN28 = 28,
    GPIO_PIN29 = 29,
    GPIO_PIN30 = 30,
    GPIO_PIN31 = 31
} airspy_gpio_pin_t;

#ifdef __cplusplus
} // __cplusplus defined.
#endif

#endif//__AIRSPY_COMMANDS_H__
