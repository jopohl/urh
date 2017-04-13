//
// Copyright 2015 Ettus Research LLC
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

#ifndef INCLUDED_UHD_USRP_H
#define INCLUDED_UHD_USRP_H

#include <uhd/config.h>
#include <uhd/error.h>
#include <uhd/types/metadata.h>
#include <uhd/types/ranges.h>
#include <uhd/types/sensors.h>
#include <uhd/types/string_vector.h>
#include <uhd/types/tune_request.h>
#include <uhd/types/tune_result.h>
#include <uhd/types/usrp_info.h>
#include <uhd/usrp/mboard_eeprom.h>
#include <uhd/usrp/dboard_eeprom.h>
#include <uhd/usrp/subdev_spec.h>

#include <stdbool.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

//! Register info
typedef struct {
    size_t bitwidth;
    bool readable;
    bool writable;
} uhd_usrp_register_info_t;

/*
 * Streamers
 */

//! A struct of parameters to construct a stream.
/*!
 * See uhd::stream_args_t for more details.
 */
typedef struct {
    //! Format of host memory
    char* cpu_format;
    //! Over-the-wire format
    char* otw_format;
    //! Other stream args
    char* args;
    //! Array that lists channels
    size_t* channel_list;
    //! Number of channels
    int n_channels;
} uhd_stream_args_t;

//! How streaming is issued to the device
/*!
 * See uhd::stream_cmd_t for more details.
 */
typedef enum {
    //! Stream samples indefinitely
    UHD_STREAM_MODE_START_CONTINUOUS   = 97,
    //! End continuous streaming
    UHD_STREAM_MODE_STOP_CONTINUOUS    = 111,
    //! Stream some number of samples and finish
    UHD_STREAM_MODE_NUM_SAMPS_AND_DONE = 100,
    //! Stream some number of samples but expect more
    UHD_STREAM_MODE_NUM_SAMPS_AND_MORE = 109
} uhd_stream_mode_t;

//! Define how device streams to host
/*!
 * See uhd::stream_cmd_t for more details.
 */
typedef struct {
    //! How streaming is issued to the device
    uhd_stream_mode_t stream_mode;
    //! Number of samples
    size_t num_samps;
    //! Stream now?
    bool stream_now;
    //! If not now, then full seconds into future to stream
    time_t time_spec_full_secs;
    //! If not now, then fractional seconds into future to stream
    double time_spec_frac_secs;
} uhd_stream_cmd_t;

struct uhd_rx_streamer;
struct uhd_tx_streamer;

//! C-level interface for working with an RX streamer
/*!
 * See uhd::rx_streamer for more details.
 */
typedef struct uhd_rx_streamer* uhd_rx_streamer_handle;

//! C-level interface for working with a TX streamer
/*!
 * See uhd::tx_streamer for more details.
 */
typedef struct uhd_tx_streamer* uhd_tx_streamer_handle;

#ifdef __cplusplus
extern "C" {
#endif

/*
 * RX Streamer
 */

//! Create an RX streamer handle.
/*!
 * NOTE: Using this streamer before passing it into uhd_usrp_get_rx_stream()
 * will result in undefined behavior.
 */
UHD_API uhd_error uhd_rx_streamer_make(
    uhd_rx_streamer_handle *h
);

//! Free an RX streamer handle.
/*!
 * NOTE: Using a streamer after passing it into this function will result
 * in a segmentation fault.
 */
UHD_API uhd_error uhd_rx_streamer_free(
    uhd_rx_streamer_handle *h
);

//! Get the number of channels associated with this streamer
UHD_API uhd_error uhd_rx_streamer_num_channels(
    uhd_rx_streamer_handle h,
    size_t *num_channels_out
);

//! Get the max number of samples per buffer per packet
UHD_API uhd_error uhd_rx_streamer_max_num_samps(
    uhd_rx_streamer_handle h,
    size_t *max_num_samps_out
);

//! Receive buffers containing samples into the given RX streamer
/*!
 * See uhd::rx_streamer::recv() for more details.
 *
 * \param h RX streamer handle
 * \param buffs pointer to buffers in which to receive samples
 * \param samps_per_buff max number of samples per buffer
 * \param md handle to RX metadata in which to receive results
 * \param timeout timeout in seconds to wait for a packet
 * \param one_packet send a single packet
 * \param items_recvd pointer to output variable for number of samples received
 */
UHD_API uhd_error uhd_rx_streamer_recv(
    uhd_rx_streamer_handle h,
    void** buffs,
    size_t samps_per_buff,
    uhd_rx_metadata_handle *md,
    double timeout,
    bool one_packet,
    size_t *items_recvd
);

//! Issue the given stream command
/*!
 * See uhd::rx_streamer::issue_stream_cmd() for more details.
 */
UHD_API uhd_error uhd_rx_streamer_issue_stream_cmd(
    uhd_rx_streamer_handle h,
    const uhd_stream_cmd_t *stream_cmd
);

//! Get the last error reported by the RX streamer
/*!
 * NOTE: This will overwrite the string currently in error_out before
 * using it to return its error.
 *
 * \param h RX streamer handle
 * \param error_out string buffer in which to place error
 * \param strbuffer_len buffer size
 */
UHD_API uhd_error uhd_rx_streamer_last_error(
    uhd_rx_streamer_handle h,
    char* error_out,
    size_t strbuffer_len
);

/*
 * TX Streamer
 */

//! Create an TX streamer handle.
/*!
 * NOTE: Using this streamer before passing it into uhd_usrp_get_tx_stream()
 * will result in undefined behavior.
 */
UHD_API uhd_error uhd_tx_streamer_make(
    uhd_tx_streamer_handle *h
);

//! Free an TX streamer handle.
/*!
 * NOTE: Using a streamer after passing it into this function will result
 * in a segmentation fault.
 */
UHD_API uhd_error uhd_tx_streamer_free(
    uhd_tx_streamer_handle *h
);

//! Get the number of channels associated with this streamer
UHD_API uhd_error uhd_tx_streamer_num_channels(
    uhd_tx_streamer_handle h,
    size_t *num_channels_out
);

//! Get the max number of samples per buffer per packet
UHD_API uhd_error uhd_tx_streamer_max_num_samps(
    uhd_tx_streamer_handle h,
    size_t *max_num_samps_out
);

//! Send buffers containing samples described by the metadata
/*!
 * See uhd::tx_streamer::send() for more details.
 *
 * \param h TX streamer handle
 * \param buffs pointer to buffers containing samples to send
 * \param samps_per_buff max number of samples per buffer
 * \param md handle to TX metadata
 * \param timeout timeout in seconds to wait for a packet
 * \param items_sent pointer to output variable for number of samples send
 */
UHD_API uhd_error uhd_tx_streamer_send(
    uhd_tx_streamer_handle h,
    const void **buffs,
    size_t samps_per_buff,
    uhd_tx_metadata_handle *md,
    double timeout,
    size_t *items_sent
);

//! Receive an asynchronous message from this streamer
/*!
 * See uhd::tx_streamer::recv_async_msg() for more details.
 */
UHD_API uhd_error uhd_tx_streamer_recv_async_msg(
    uhd_tx_streamer_handle h,
    uhd_async_metadata_handle *md,
    double timeout,
    bool *valid
);

//! Get the last error reported by the TX streamer
/*!
 * NOTE: This will overwrite the string currently in error_out before
 * using it to return its error.
 *
 * \param h TX streamer handle
 * \param error_out string buffer in which to place error
 * \param strbuffer_len buffer size
 */
UHD_API uhd_error uhd_tx_streamer_last_error(
    uhd_tx_streamer_handle h,
    char* error_out,
    size_t strbuffer_len
);

#ifdef __cplusplus
}
#endif

/****************************************************************************
 * Public Datatypes for USRP / streamer handling.
 ***************************************************************************/
struct uhd_usrp;

//! C-level interface for working with a USRP device
/*
 * See uhd::usrp::multi_usrp for more details.
 *
 * NOTE: You must pass this handle into uhd_usrp_make before using it.
 */
typedef struct uhd_usrp* uhd_usrp_handle;

/****************************************************************************
 * USRP Make / Free API calls
 ***************************************************************************/
#ifdef __cplusplus
extern "C" {
#endif

//! Find all connected USRP devices.
/*!
 * See uhd::device::find() for more details.
 */
UHD_API uhd_error uhd_usrp_find(
    const char* args,
    uhd_string_vector_handle *strings_out
);

//! Create a USRP handle.
/*!
 * \param h the handle
 * \param args device args (e.g. "type=x300")
 */
UHD_API uhd_error uhd_usrp_make(
    uhd_usrp_handle *h,
    const char *args
);

//! Safely destroy the USRP object underlying the handle.
/*!
 * NOTE: Attempting to use a USRP handle after passing it into this function
 * will result in a segmentation fault.
 */
UHD_API uhd_error uhd_usrp_free(
    uhd_usrp_handle *h
);

//! Get the last error reported by the USRP handle
UHD_API uhd_error uhd_usrp_last_error(
    uhd_usrp_handle h,
    char* error_out,
    size_t strbuffer_len
);

//! Create RX streamer from a USRP handle and given stream args
UHD_API uhd_error uhd_usrp_get_rx_stream(
    uhd_usrp_handle h,
    uhd_stream_args_t *stream_args,
    uhd_rx_streamer_handle h_out
);

//! Create TX streamer from a USRP handle and given stream args
UHD_API uhd_error uhd_usrp_get_tx_stream(
    uhd_usrp_handle h,
    uhd_stream_args_t *stream_args,
    uhd_tx_streamer_handle h_out
);

/****************************************************************************
 * multi_usrp API calls
 ***************************************************************************/

//! Get RX info from the USRP device
/*!
 * NOTE: After calling this function, uhd_usrp_rx_info_free() must be called on info_out.
 */
UHD_API uhd_error uhd_usrp_get_rx_info(
    uhd_usrp_handle h,
    size_t chan,
    uhd_usrp_rx_info_t *info_out
);

//! Get TX info from the USRP device
/*!
 * NOTE: After calling this function, uhd_usrp_tx_info_free() must be called on info_out.
 */
UHD_API uhd_error uhd_usrp_get_tx_info(
    uhd_usrp_handle h,
    size_t chan,
    uhd_usrp_tx_info_t *info_out
);

/****************************************************************************
 * Motherboard methods
 ***************************************************************************/

//! Set the master clock rate.
/*!
 * See uhd::usrp::multi_usrp::set_master_clock_rate() for more details.
 */
UHD_API uhd_error uhd_usrp_set_master_clock_rate(
    uhd_usrp_handle h,
    double rate,
    size_t mboard
);

//! Get the master clock rate.
/*!
 * See uhd::usrp::multi_usrp::get_master_clock_rate() for more details.
 */
UHD_API uhd_error uhd_usrp_get_master_clock_rate(
    uhd_usrp_handle h,
    size_t mboard,
    double *clock_rate_out
);

//! Get a pretty-print representation of the USRP device.
/*!
 * See uhd::usrp::multi_usrp::get_pp_string() for more details.
 */
UHD_API uhd_error uhd_usrp_get_pp_string(
    uhd_usrp_handle h,
    char* pp_string_out,
    size_t strbuffer_len
);

//! Get the motherboard name for the given device
/*!
 * See uhd::usrp::multi_usrp::get_mboard_name() for more details.
 */
UHD_API uhd_error uhd_usrp_get_mboard_name(
    uhd_usrp_handle h,
    size_t mboard,
    char* mboard_name_out,
    size_t strbuffer_len
);

//! Get the USRP device's current internal time
/*!
 * See uhd::usrp::multi_usrp::get_time_now() for more details.
 */
UHD_API uhd_error uhd_usrp_get_time_now(
    uhd_usrp_handle h,
    size_t mboard,
    time_t *full_secs_out,
    double *frac_secs_out
);

//! Get the time when this device's last PPS pulse occurred
/*!
 * See uhd::usrp::multi_usrp::get_time_last_pps() for more details.
 */
UHD_API uhd_error uhd_usrp_get_time_last_pps(
    uhd_usrp_handle h,
    size_t mboard,
    time_t *full_secs_out,
    double *frac_secs_out
);

//! Set the USRP device's time
/*!
 * See uhd::usrp::multi_usrp::set_time_now() for more details.
 */
UHD_API uhd_error uhd_usrp_set_time_now(
    uhd_usrp_handle h,
    time_t full_secs,
    double frac_secs,
    size_t mboard
);

//! Set the USRP device's time to the given value upon the next PPS detection
/*!
 * See uhd::usrp::multi_usrp::set_time_next_pps() for more details.
 */
UHD_API uhd_error uhd_usrp_set_time_next_pps(
    uhd_usrp_handle h,
    time_t full_secs,
    double frac_secs,
    size_t mboard
);

//! Synchronize the time across all motherboards
/*!
 * See uhd::usrp::multi_usrp::set_time_unknown_pps() for more details.
 */
UHD_API uhd_error uhd_usrp_set_time_unknown_pps(
    uhd_usrp_handle h,
    time_t full_secs,
    double frac_secs
);

//! Are all motherboard times synchronized?
UHD_API uhd_error uhd_usrp_get_time_synchronized(
    uhd_usrp_handle h,
    bool *result_out
);

//! Set the time at which timed commands will take place
/*!
 * See uhd::usrp::multi_usrp::set_command_time() for more details.
 */
UHD_API uhd_error uhd_usrp_set_command_time(
    uhd_usrp_handle h,
    time_t full_secs,
    double frac_secs,
    size_t mboard
);

//! Clear the command time so that commands are sent ASAP
UHD_API uhd_error uhd_usrp_clear_command_time(
    uhd_usrp_handle h,
    size_t mboard
);

//! Set the time source for the given device
/*!
 * See uhd::usrp::multi_usrp::set_time_source() for more details.
 */
UHD_API uhd_error uhd_usrp_set_time_source(
    uhd_usrp_handle h,
    const char* time_source,
    size_t mboard
);

//! Get the time source for the given device
/*!
 * See uhd::usrp::multi_usrp::get_time_source() for more details.
 */
UHD_API uhd_error uhd_usrp_get_time_source(
    uhd_usrp_handle h,
    size_t mboard,
    char* time_source_out,
    size_t strbuffer_len
);

//! Get a list of time sources for the given device
UHD_API uhd_error uhd_usrp_get_time_sources(
    uhd_usrp_handle h,
    size_t mboard,
    uhd_string_vector_handle *time_sources_out
);

//! Set the given device's clock source
/*!
 * See uhd::usrp::multi_usrp::set_clock_source() for more details.
 */
UHD_API uhd_error uhd_usrp_set_clock_source(
    uhd_usrp_handle h,
    const char* clock_source,
    size_t mboard
);

//! Get the given device's clock source
/*!
 * See uhd::usrp::multi_usrp::get_clock_source() for more details.
 */
UHD_API uhd_error uhd_usrp_get_clock_source(
    uhd_usrp_handle h,
    size_t mboard,
    char* clock_source_out,
    size_t strbuffer_len
);

//! Get a list of clock sources for the given device
UHD_API uhd_error uhd_usrp_get_clock_sources(
    uhd_usrp_handle h,
    size_t mboard,
    uhd_string_vector_handle *clock_sources_out
);

//! Enable or disable sending the clock source to an output connector
/*!
 * See uhd::usrp::set_clock_source_out() for more details.
 */
UHD_API uhd_error uhd_usrp_set_clock_source_out(
    uhd_usrp_handle h,
    bool enb,
    size_t mboard
);

//! Enable or disable sending the time source to an output connector
/*!
 * See uhd::usrp::set_time_source_out() for more details.
 */
UHD_API uhd_error uhd_usrp_set_time_source_out(
    uhd_usrp_handle h,
    bool enb,
    size_t mboard
);

//! Get the number of devices associated with the given USRP handle
UHD_API uhd_error uhd_usrp_get_num_mboards(
    uhd_usrp_handle h,
    size_t *num_mboards_out
);

//! Get the value associated with the given sensor name
UHD_API uhd_error uhd_usrp_get_mboard_sensor(
    uhd_usrp_handle h,
    const char* name,
    size_t mboard,
    uhd_sensor_value_handle *sensor_value_out
);

//! Get a list of motherboard sensors for the given device
UHD_API uhd_error uhd_usrp_get_mboard_sensor_names(
    uhd_usrp_handle h,
    size_t mboard,
    uhd_string_vector_handle *mboard_sensor_names_out
);

//! Perform a write on a user configuration register bus
/*!
 * See uhd::usrp::multi_usrp::set_user_register() for more details.
 */
UHD_API uhd_error uhd_usrp_set_user_register(
    uhd_usrp_handle h,
    uint8_t addr,
    uint32_t data,
    size_t mboard
);

/****************************************************************************
 * EEPROM access methods
 ***************************************************************************/

//! Get a handle for the given motherboard's EEPROM
UHD_API uhd_error uhd_usrp_get_mboard_eeprom(
    uhd_usrp_handle h,
    uhd_mboard_eeprom_handle mb_eeprom,
    size_t mboard
);

//! Set values in the given motherboard's EEPROM
UHD_API uhd_error uhd_usrp_set_mboard_eeprom(
    uhd_usrp_handle h,
    uhd_mboard_eeprom_handle mb_eeprom,
    size_t mboard
);

//! Get a handle for the given device's daughterboard EEPROM
UHD_API uhd_error uhd_usrp_get_dboard_eeprom(
    uhd_usrp_handle h,
    uhd_dboard_eeprom_handle db_eeprom,
    const char* unit,
    const char* slot,
    size_t mboard
);

//! Set values in the given daughterboard's EEPROM
UHD_API uhd_error uhd_usrp_set_dboard_eeprom(
    uhd_usrp_handle h,
    uhd_dboard_eeprom_handle db_eeprom,
    const char* unit,
    const char* slot,
    size_t mboard
);

/****************************************************************************
 * RX methods
 ***************************************************************************/

//! Map the given device's RX frontend to a channel
/*!
 * See uhd::usrp::multi_usrp::set_rx_subdev_spec() for more details.
 */
UHD_API uhd_error uhd_usrp_set_rx_subdev_spec(
    uhd_usrp_handle h,
    uhd_subdev_spec_handle subdev_spec,
    size_t mboard
);

//! Get the RX frontend specification for the given device
UHD_API uhd_error uhd_usrp_get_rx_subdev_spec(
    uhd_usrp_handle h,
    size_t mboard,
    uhd_subdev_spec_handle subdev_spec_out
);

//! Get the number of RX channels for the given handle
UHD_API uhd_error uhd_usrp_get_rx_num_channels(
    uhd_usrp_handle h,
    size_t *num_channels_out
);

//! Get the name for the RX frontend
UHD_API uhd_error uhd_usrp_get_rx_subdev_name(
    uhd_usrp_handle h,
    size_t chan,
    char* rx_subdev_name_out,
    size_t strbuffer_len
);

//! Set the given RX channel's sample rate (in Sps)
UHD_API uhd_error uhd_usrp_set_rx_rate(
    uhd_usrp_handle h,
    double rate,
    size_t chan
);

//! Get the given RX channel's sample rate (in Sps)
UHD_API uhd_error uhd_usrp_get_rx_rate(
    uhd_usrp_handle h,
    size_t chan,
    double *rate_out
);

//! Get a range of possible RX rates for the given channel
UHD_API uhd_error uhd_usrp_get_rx_rates(
    uhd_usrp_handle h,
    size_t chan,
    uhd_meta_range_handle rates_out
);

//! Set the given channel's center RX frequency
UHD_API uhd_error uhd_usrp_set_rx_freq(
    uhd_usrp_handle h,
    uhd_tune_request_t *tune_request,
    size_t chan,
    uhd_tune_result_t *tune_result
);

//! Get the given channel's center RX frequency
UHD_API uhd_error uhd_usrp_get_rx_freq(
    uhd_usrp_handle h,
    size_t chan,
    double *freq_out
);

//! Get all possible center frequency ranges for the given channel
/*!
 * See uhd::usrp::multi_usrp::get_rx_freq_range() for more details.
 */
UHD_API uhd_error uhd_usrp_get_rx_freq_range(
    uhd_usrp_handle h,
    size_t chan,
    uhd_meta_range_handle freq_range_out
);

//! Get all possible RF frequency ranges for the given channel's RX RF frontend
UHD_API uhd_error uhd_usrp_get_fe_rx_freq_range(
    uhd_usrp_handle h,
    size_t chan,
    uhd_meta_range_handle freq_range_out
);

//! Set the RX gain for the given channel and name
UHD_API uhd_error uhd_usrp_set_rx_gain(
    uhd_usrp_handle h,
    double gain,
    size_t chan,
    const char *gain_name
);

//! Set the normalized RX gain [0.0, 1.0] for the given channel
/*!
 * See uhd::usrp::multi_usrp::set_normalized_rx_gain() for more details.
 */
UHD_API uhd_error uhd_usrp_set_normalized_rx_gain(
    uhd_usrp_handle h,
    double gain,
    size_t chan
);

//! Enable or disable the given channel's RX AGC module
/*!
 * See uhd::usrp::multi_usrp::set_rx_agc() for more details.
 */
UHD_API uhd_error uhd_usrp_set_rx_agc(
    uhd_usrp_handle h,
    bool enable,
    size_t chan
);

//! Get the given channel's RX gain
UHD_API uhd_error uhd_usrp_get_rx_gain(
    uhd_usrp_handle h,
    size_t chan,
    const char *gain_name,
    double *gain_out
);

//! Get the given channel's normalized RX gain [0.0, 1.0]
/*!
 * See uhd::usrp::multi_usrp::get_normalized_rx_gain() for more details.
 */
UHD_API uhd_error uhd_usrp_get_normalized_rx_gain(
    uhd_usrp_handle h,
    size_t chan,
    double *gain_out
);

//! Get all possible gain ranges for the given channel and name
UHD_API uhd_error uhd_usrp_get_rx_gain_range(
    uhd_usrp_handle h,
    const char* name,
    size_t chan,
    uhd_meta_range_handle gain_range_out
);

//! Get a list of RX gain names for the given channel
UHD_API uhd_error uhd_usrp_get_rx_gain_names(
    uhd_usrp_handle h,
    size_t chan,
    uhd_string_vector_handle *gain_names_out
);

//! Set the RX antenna for the given channel
UHD_API uhd_error uhd_usrp_set_rx_antenna(
    uhd_usrp_handle h,
    const char* ant,
    size_t chan
);

//! Get the RX antenna for the given channel
UHD_API uhd_error uhd_usrp_get_rx_antenna(
    uhd_usrp_handle h,
    size_t chan,
    char* ant_out,
    size_t strbuffer_len
);

//! Get a list of RX antennas associated with the given channels
UHD_API uhd_error uhd_usrp_get_rx_antennas(
    uhd_usrp_handle h,
    size_t chan,
    uhd_string_vector_handle *antennas_out
);

//! Get a list of RX sensors associated with the given channels
UHD_API uhd_error uhd_usrp_get_rx_sensor_names(
    uhd_usrp_handle h,
    size_t chan,
    uhd_string_vector_handle *sensor_names_out
);

//! Set the bandwidth for the given channel's RX frontend
UHD_API uhd_error uhd_usrp_set_rx_bandwidth(
    uhd_usrp_handle h,
    double bandwidth,
    size_t chan
);

//! Get the bandwidth for the given channel's RX frontend
UHD_API uhd_error uhd_usrp_get_rx_bandwidth(
    uhd_usrp_handle h,
    size_t chan,
    double *bandwidth_out
);

//! Get all possible bandwidth ranges for the given channel's RX frontend
UHD_API uhd_error uhd_usrp_get_rx_bandwidth_range(
    uhd_usrp_handle h,
    size_t chan,
    uhd_meta_range_handle bandwidth_range_out
);

//! Get the value for the given RX sensor
UHD_API uhd_error uhd_usrp_get_rx_sensor(
    uhd_usrp_handle h,
    const char* name,
    size_t chan,
    uhd_sensor_value_handle *sensor_value_out
);

//! Enable or disable RX DC offset correction for the given channel
/*!
 * See uhd::usrp::multi_usrp::set_rx_dc_offset() for more details.
 */
UHD_API uhd_error uhd_usrp_set_rx_dc_offset_enabled(
    uhd_usrp_handle h,
    bool enb,
    size_t chan
);

//! Enable or disable RX IQ imbalance correction for the given channel
UHD_API uhd_error uhd_usrp_set_rx_iq_balance_enabled(
    uhd_usrp_handle h,
    bool enb,
    size_t chan
);

/****************************************************************************
 * TX methods
 ***************************************************************************/

//! Map the given device's TX frontend to a channel
/*!
 * See uhd::usrp::multi_usrp::set_tx_subdev_spec() for more details.
 */
UHD_API uhd_error uhd_usrp_set_tx_subdev_spec(
    uhd_usrp_handle h,
    uhd_subdev_spec_handle subdev_spec,
    size_t mboard
);

//! Get the TX frontend specification for the given device
UHD_API uhd_error uhd_usrp_get_tx_subdev_spec(
    uhd_usrp_handle h,
    size_t mboard,
    uhd_subdev_spec_handle subdev_spec_out
);

//! Get the number of TX channels for the given handle
UHD_API uhd_error uhd_usrp_get_tx_num_channels(
    uhd_usrp_handle h,
    size_t *num_channels_out
);

//! Get the name for the RX frontend
UHD_API uhd_error uhd_usrp_get_tx_subdev_name(
    uhd_usrp_handle h,
    size_t chan,
    char* tx_subdev_name_out,
    size_t strbuffer_len
);

//! Set the given RX channel's sample rate (in Sps)
UHD_API uhd_error uhd_usrp_set_tx_rate(
    uhd_usrp_handle h,
    double rate,
    size_t chan
);

//! Get the given RX channel's sample rate (in Sps)
UHD_API uhd_error uhd_usrp_get_tx_rate(
    uhd_usrp_handle h,
    size_t chan,
    double *rate_out
);

//! Get a range of possible RX rates for the given channel
UHD_API uhd_error uhd_usrp_get_tx_rates(
    uhd_usrp_handle h,
    size_t chan,
    uhd_meta_range_handle rates_out
);

//! Set the given channel's center TX frequency
UHD_API uhd_error uhd_usrp_set_tx_freq(
    uhd_usrp_handle h,
    uhd_tune_request_t *tune_request,
    size_t chan,
    uhd_tune_result_t *tune_result
);

//! Get the given channel's center TX frequency
UHD_API uhd_error uhd_usrp_get_tx_freq(
    uhd_usrp_handle h,
    size_t chan,
    double *freq_out
);

//! Get all possible center frequency ranges for the given channel
/*!
 * See uhd::usrp::multi_usrp::get_rx_freq_range() for more details.
 */
UHD_API uhd_error uhd_usrp_get_tx_freq_range(
    uhd_usrp_handle h,
    size_t chan,
    uhd_meta_range_handle freq_range_out
);

//! Get all possible RF frequency ranges for the given channel's TX RF frontend
UHD_API uhd_error uhd_usrp_get_fe_tx_freq_range(
    uhd_usrp_handle h,
    size_t chan,
    uhd_meta_range_handle freq_range_out
);

//! Set the TX gain for the given channel and name
UHD_API uhd_error uhd_usrp_set_tx_gain(
    uhd_usrp_handle h,
    double gain,
    size_t chan,
    const char *gain_name
);

//! Set the normalized TX gain [0.0, 1.0] for the given channel
/*!
 * See uhd::usrp::multi_usrp::set_normalized_tx_gain() for more details.
 */
UHD_API uhd_error uhd_usrp_set_normalized_tx_gain(
    uhd_usrp_handle h,
    double gain,
    size_t chan
);

//! Get all possible gain ranges for the given channel and name
UHD_API uhd_error uhd_usrp_get_tx_gain_range(
    uhd_usrp_handle h,
    const char* name,
    size_t chan,
    uhd_meta_range_handle gain_range_out
);

//! Get the given channel's RX gain
UHD_API uhd_error uhd_usrp_get_tx_gain(
    uhd_usrp_handle h,
    size_t chan,
    const char *gain_name,
    double *gain_out
);

//! Get the given channel's normalized TX gain [0.0, 1.0]
/*!
 * See uhd::usrp::multi_usrp::get_normalized_tx_gain() for more details.
 */
UHD_API uhd_error uhd_usrp_get_normalized_tx_gain(
    uhd_usrp_handle h,
    size_t chan,
    double *gain_out
);

//! Get a list of TX gain names for the given channel
UHD_API uhd_error uhd_usrp_get_tx_gain_names(
    uhd_usrp_handle h,
    size_t chan,
    uhd_string_vector_handle *gain_names_out
);

//! Set the TX antenna for the given channel
UHD_API uhd_error uhd_usrp_set_tx_antenna(
    uhd_usrp_handle h,
    const char* ant,
    size_t chan
);

//! Get the TX antenna for the given channel
UHD_API uhd_error uhd_usrp_get_tx_antenna(
    uhd_usrp_handle h,
    size_t chan,
    char* ant_out,
    size_t strbuffer_len
);

//! Get a list of tx antennas associated with the given channels
UHD_API uhd_error uhd_usrp_get_tx_antennas(
    uhd_usrp_handle h,
    size_t chan,
    uhd_string_vector_handle *antennas_out
);

//! Set the bandwidth for the given channel's TX frontend
UHD_API uhd_error uhd_usrp_set_tx_bandwidth(
    uhd_usrp_handle h,
    double bandwidth,
    size_t chan
);

//! Get the bandwidth for the given channel's TX frontend
UHD_API uhd_error uhd_usrp_get_tx_bandwidth(
    uhd_usrp_handle h,
    size_t chan,
    double *bandwidth_out
);

//! Get all possible bandwidth ranges for the given channel's TX frontend
UHD_API uhd_error uhd_usrp_get_tx_bandwidth_range(
    uhd_usrp_handle h,
    size_t chan,
    uhd_meta_range_handle bandwidth_range_out
);

//! Get the value for the given TX sensor
UHD_API uhd_error uhd_usrp_get_tx_sensor(
    uhd_usrp_handle h,
    const char* name,
    size_t chan,
    uhd_sensor_value_handle *sensor_value_out
);

//! Get a list of TX sensors associated with the given channels
UHD_API uhd_error uhd_usrp_get_tx_sensor_names(
    uhd_usrp_handle h,
    size_t chan,
    uhd_string_vector_handle *sensor_names_out
);

//! Enable or disable TX DC offset correction for the given channel
/*!
 * See uhd::usrp::multi_usrp::set_tx_dc_offset() for more details.
 */
UHD_API uhd_error uhd_usrp_set_tx_dc_offset_enabled(
    uhd_usrp_handle h,
    bool enb,
    size_t chan
);

//! Enable or disable TX IQ imbalance correction for the given channel
UHD_API uhd_error uhd_usrp_set_tx_iq_balance_enabled(
    uhd_usrp_handle h,
    bool enb,
    size_t chan
);

/****************************************************************************
 * GPIO methods
 ***************************************************************************/

//! Get a list of GPIO banks associated with the given channels
UHD_API uhd_error uhd_usrp_get_gpio_banks(
    uhd_usrp_handle h,
    size_t mboard,
    uhd_string_vector_handle *gpio_banks_out
);

//! Set a GPIO attribute for a given GPIO bank
/*!
 * See uhd::usrp::multi_usrp::set_gpio_attr() for more details.
 */
UHD_API uhd_error uhd_usrp_set_gpio_attr(
    uhd_usrp_handle h,
    const char* bank,
    const char* attr,
    uint32_t value,
    uint32_t mask,
    size_t mboard
);

//! Get a GPIO attribute on a particular GPIO bank
/*!
 * See uhd::usrp::multi_usrp::get_gpio_attr() for more details.
 */
UHD_API uhd_error uhd_usrp_get_gpio_attr(
    uhd_usrp_handle h,
    const char* bank,
    const char* attr,
    size_t mboard,
    uint32_t *attr_out
);

//! Enumerate the full paths of USRP registers available for read/write
UHD_API uhd_error uhd_usrp_enumerate_registers(
    uhd_usrp_handle h,
    size_t mboard,
    uhd_string_vector_handle *registers_out
);

//! Get more information about a low-level device register
UHD_API uhd_error uhd_usrp_get_register_info(
    uhd_usrp_handle h,
    const char* path,
    size_t mboard,
    uhd_usrp_register_info_t *register_info_out
);

//! Write a low-level register field for a device register in the USRP hardware
UHD_API uhd_error uhd_usrp_write_register(
    uhd_usrp_handle h,
    const char* path,
    uint32_t field,
    uint64_t value,
    size_t mboard
);

//! Read a low-level register field from a device register in the USRP hardware
UHD_API uhd_error uhd_usrp_read_register(
    uhd_usrp_handle h,
    const char* path,
    uint32_t field,
    size_t mboard,
    uint64_t *value_out
);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDED_UHD_USRP_H */
