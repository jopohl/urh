/*
 * Copyright 2015 Ettus Research
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef INCLUDED_UHD_TYPES_METADATA_H
#define INCLUDED_UHD_TYPES_METADATA_H

#include <uhd/config.h>
#include <uhd/error.h>

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

#ifdef __cplusplus
#include <uhd/types/metadata.hpp>
#include <string>

struct uhd_rx_metadata_t {
    uhd::rx_metadata_t rx_metadata_cpp;
    std::string last_error;
};

struct uhd_tx_metadata_t {
    uhd::tx_metadata_t tx_metadata_cpp;
    std::string last_error;
};

struct uhd_async_metadata_t {
    uhd::async_metadata_t async_metadata_cpp;
    std::string last_error;
};

extern "C" {
#else
struct uhd_rx_metadata_t;
struct uhd_tx_metadata_t;
struct uhd_async_metadata_t;
#endif

//! RX metadata interface for describing sent IF data.
/*!
 * See uhd::rx_metadata_t for details.
 *
 * NOTE: Using this handle before calling uhd_rx_metadata_make() will
 * result in undefined behavior.
 */
typedef struct uhd_rx_metadata_t*    uhd_rx_metadata_handle;

//! TX metadata interface for describing received IF data.
/*!
 * See uhd::tx_metadata_t for details.
 *
 * NOTE: Using this handle before calling uhd_tx_metadata_make() will
 * result in undefined behavior.
 */
typedef struct uhd_tx_metadata_t*    uhd_tx_metadata_handle;

//! Interface for describing transmit-related events.
/*!
 * See uhd::async_metadata_t for details.
 *
 * NOTE: Using this handle before calling uhd_async_metadata_make() will
 * result in undefined behavior.
 */
typedef struct uhd_async_metadata_t* uhd_async_metadata_handle;

//! Error condition on a receive call
/*!
 * See uhd::rx_metadata_t::error_code_t for more details.
 */
typedef enum {
    //! No error code associated with this metadata
    UHD_RX_METADATA_ERROR_CODE_NONE         = 0x0,
    //! No packet received, implementation timed out
    UHD_RX_METADATA_ERROR_CODE_TIMEOUT      = 0x1,
    //! A stream command was issued in the past
    UHD_RX_METADATA_ERROR_CODE_LATE_COMMAND = 0x2,
    //! Expected another stream command
    UHD_RX_METADATA_ERROR_CODE_BROKEN_CHAIN = 0x4,
    //! Overflow or sequence error
    UHD_RX_METADATA_ERROR_CODE_OVERFLOW     = 0x8,
    //! Multi-channel alignment failed
    UHD_RX_METADATA_ERROR_CODE_ALIGNMENT    = 0xC,
    //! The packet could not be parsed
    UHD_RX_METADATA_ERROR_CODE_BAD_PACKET   = 0xF
} uhd_rx_metadata_error_code_t;


//! Create a new RX metadata handle
UHD_API uhd_error uhd_rx_metadata_make(
    uhd_rx_metadata_handle* handle
);

//! Free an RX metadata handle
/*!
 * Using a handle after freeing it here will result in a segmentation fault.
 */
UHD_API uhd_error uhd_rx_metadata_free(
    uhd_rx_metadata_handle* handle
);

//! Has time specification?
UHD_API uhd_error uhd_rx_metadata_has_time_spec(
    uhd_rx_metadata_handle h,
    bool *result_out
);

//! Time of first sample
UHD_API uhd_error uhd_rx_metadata_time_spec(
    uhd_rx_metadata_handle h,
    time_t *full_secs_out,
    double *frac_secs_out
);

//! Fragmentation flag
UHD_API uhd_error uhd_rx_metadata_more_fragments(
    uhd_rx_metadata_handle h,
    bool *result_out
);

//! Fragmentation offset
UHD_API uhd_error uhd_rx_metadata_fragment_offset(
    uhd_rx_metadata_handle h,
    size_t *fragment_offset_out
);

//! Start of burst?
UHD_API uhd_error uhd_rx_metadata_start_of_burst(
    uhd_rx_metadata_handle h,
    bool *result_out
);

//! End of burst?
UHD_API uhd_error uhd_rx_metadata_end_of_burst(
    uhd_rx_metadata_handle h,
    bool *result_out
);

//! Result out of sequence?
UHD_API uhd_error uhd_rx_metadata_out_of_sequence(
    uhd_rx_metadata_handle h,
    bool *result_out
);

//! Return a pretty-print representation of this metadata.
/*!
 * NOTE: This function will overwrite any string in the given buffer
 * before inserting the pp_string.
 *
 * \param h metadata handle
 * \param pp_string_out string buffer for pp_string
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_rx_metadata_to_pp_string(
    uhd_rx_metadata_handle h,
    char* pp_string_out,
    size_t strbuffer_len
);

//! Get the last error state of the RX metadata object.
UHD_API uhd_error uhd_rx_metadata_error_code(
    uhd_rx_metadata_handle h,
    uhd_rx_metadata_error_code_t *error_code_out
);

//! Get a string representation of the last error state of the RX metadata object.
/*!
 * NOTES:
 * <ul>
 * <li>This is different from the error that can be retrieved with
 *     uhd_rx_metadata_last_error. See uhd::rx_metadata_t::strerror() for details.</li>
 * <li>This function will overwrite any string in the given buffer before
 *     inserting the error string.</li>
 * </ul>
 *
 * \param h metadata handle
 * \param strerror_out string buffer for strerror
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_rx_metadata_strerror(
    uhd_rx_metadata_handle h,
    char* strerror_out,
    size_t strbuffer_len
);

//! Get the last error logged by the RX metadata object.
/*!
 * NOTES:
 * <ul>
 * <li>This is different from the error that can be retrieved with
 *     uhd_rx_metadata_strerror(). See <uhd/error.h> for details.</li>
 * <li>This function will overwrite any string in the given buffer before
 *     inserting the error string.</li>
 * </ul>
 *
 * \param h metadata handle
 * \param error_out string buffer for error
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_rx_metadata_last_error(
    uhd_rx_metadata_handle h,
    char* error_out,
    size_t strbuffer_len
);

//! Create a new TX metadata handle
UHD_API uhd_error uhd_tx_metadata_make(
    uhd_tx_metadata_handle* handle,
    bool has_time_spec,
    time_t full_secs,
    double frac_secs,
    bool start_of_burst,
    bool end_of_burst
);


//! Free an TX metadata handle
/*!
 * Using a handle after freeing it here will result in a segmentation fault.
 */
UHD_API uhd_error uhd_tx_metadata_free(
    uhd_tx_metadata_handle* handle
);

//! Has time specification?
UHD_API uhd_error uhd_tx_metadata_has_time_spec(
    uhd_tx_metadata_handle h,
    bool *result_out
);

//! Get time specification
UHD_API uhd_error uhd_tx_metadata_time_spec(
    uhd_tx_metadata_handle h,
    time_t *full_secs_out,
    double *frac_secs_out
);

//! Start of burst?
UHD_API uhd_error uhd_tx_metadata_start_of_burst(
    uhd_tx_metadata_handle h,
    bool *result_out
);

//! End of burst?
UHD_API uhd_error uhd_tx_metadata_end_of_burst(
    uhd_tx_metadata_handle h,
    bool *result_out
);

//! Get the last error logged by the TX metadata object.
/*!
 * NOTE: This function will overwrite any string in the given buffer before
 * inserting the error string.
 *
 * \param h metadata handle
 * \param error_out string buffer for error
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_tx_metadata_last_error(
    uhd_tx_metadata_handle h,
    char* error_out,
    size_t strbuffer_len
);

//! The type of event for a receive async message call.
/*!
 * See uhd::async_metadata_t::event_code_t for more details.
 */
typedef enum {
    //! A burst was successfully transmitted.
    UHD_ASYNC_METADATA_EVENT_CODE_BURST_ACK           = 0x1,
    //! An internal send buffer has emptied.
    UHD_ASYNC_METADATA_EVENT_CODE_UNDERFLOW           = 0x2,
    //! Packet loss error between host and device.
    UHD_ASYNC_METADATA_EVENT_CODE_SEQ_ERROR           = 0x4,
    //! Packet had time that was late.
    UHD_ASYNC_METADATA_EVENT_CODE_TIME_ERROR          = 0x8,
    //! Underflow occurred inside a packet.
    UHD_ASYNC_METADATA_EVENT_CODE_UNDERFLOW_IN_PACKET = 0x10,
    //! Packet loss within a burst.
    UHD_ASYNC_METADATA_EVENT_CODE_SEQ_ERROR_IN_BURST  = 0x20,
    //! Some kind of custom user payload.
    UHD_ASYNC_METADATA_EVENT_CODE_USER_PAYLOAD        = 0x40
} uhd_async_metadata_event_code_t;

//! Create a new async metadata handle
UHD_API uhd_error uhd_async_metadata_make(
    uhd_async_metadata_handle* handle
);

//! Free an async metadata handle
/*!
 * Using a handle after freeing it will result in a segmentation fault.
 */
UHD_API uhd_error uhd_async_metadata_free(
    uhd_async_metadata_handle* handle
);

//! Channel number in a MIMO configuration
UHD_API uhd_error uhd_async_metadata_channel(
    uhd_async_metadata_handle h,
    size_t *channel_out
);

//! Has time specification?
UHD_API uhd_error uhd_async_metadata_has_time_spec(
    uhd_async_metadata_handle h,
    bool *result_out
);

//! Get time specification
UHD_API uhd_error uhd_async_metadata_time_spec(
    uhd_async_metadata_handle h,
    time_t *full_secs_out,
    double *frac_secs_out
);

//! Get last event code
UHD_API uhd_error uhd_async_metadata_event_code(
    uhd_async_metadata_handle h,
    uhd_async_metadata_event_code_t *event_code_out
);

//! Get payload from custom FPGA fabric
UHD_API uhd_error uhd_async_metadata_user_payload(
    uhd_async_metadata_handle h,
    uint32_t user_payload_out[4]
);

//! Get the last error logged by the async metadata object.
/*!
 * NOTE: This function will overwrite any string in the given buffer before
 * inserting the error string.
 *
 * \param h metadata handle
 * \param error_out string buffer for error
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_async_metadata_last_error(
    uhd_async_metadata_handle h,
    char* error_out,
    size_t strbuffer_len
);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDED_UHD_TYPES_METADATA_H */
