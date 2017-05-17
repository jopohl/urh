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

#ifndef INCLUDED_UHD_USRP_DBOARD_EEPROM_H
#define INCLUDED_UHD_USRP_DBOARD_EEPROM_H

#include <uhd/config.h>
#include <uhd/error.h>

#ifdef __cplusplus
#include <uhd/usrp/dboard_eeprom.hpp>
#include <string>

struct uhd_dboard_eeprom_t {
    uhd::usrp::dboard_eeprom_t dboard_eeprom_cpp;
    std::string last_error;
};

extern "C" {
#else
struct uhd_dboard_eeprom_t;
#endif

//! A C-level interface for interacting with a daughterboard EEPROM
/*!
 * See uhd::usrp::dboard_eeprom_t for more details.
 *
 * NOTE: Using a handle before passing it into uhd_dboard_eeprom_make() will
 * result in undefined behavior.
 */
typedef struct uhd_dboard_eeprom_t* uhd_dboard_eeprom_handle;

//! Create handle for a USRP daughterboard EEPROM
UHD_API uhd_error uhd_dboard_eeprom_make(
    uhd_dboard_eeprom_handle* h
);

//! Safely destroy the given handle
/*!
 * NOTE: Using a handle after passing it into this function will result in
 * a segmentation fault.
 */
UHD_API uhd_error uhd_dboard_eeprom_free(
    uhd_dboard_eeprom_handle* h
);

//! Get the ID associated with the given daughterboard as a string hex representation
UHD_API uhd_error uhd_dboard_eeprom_get_id(
    uhd_dboard_eeprom_handle h,
    char* id_out,
    size_t strbuffer_len
);

//! Set the daughterboard ID using a string hex representation
UHD_API uhd_error uhd_dboard_eeprom_set_id(
    uhd_dboard_eeprom_handle h,
    const char* id
);

//! Get the daughterboard's serial
UHD_API uhd_error uhd_dboard_eeprom_get_serial(
    uhd_dboard_eeprom_handle h,
    char* serial_out,
    size_t strbuffer_len
);

//! Set the daughterboard's serial
UHD_API uhd_error uhd_dboard_eeprom_set_serial(
    uhd_dboard_eeprom_handle h,
    const char* serial
);

//! Get the daughterboard's revision (not always present)
UHD_API uhd_error uhd_dboard_eeprom_get_revision(
    uhd_dboard_eeprom_handle h,
    int* revision_out
);

//! Set the daughterboard's revision
UHD_API uhd_error uhd_dboard_eeprom_set_revision(
    uhd_dboard_eeprom_handle h,
    int revision
);

//! Get the last error reported by the handle
UHD_API uhd_error uhd_dboard_eeprom_last_error(
    uhd_dboard_eeprom_handle h,
    char* error_out,
    size_t strbuffer_len
);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDED_UHD_USRP_DBOARD_EEPROM_H */
