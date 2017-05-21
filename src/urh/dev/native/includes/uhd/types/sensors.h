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

#ifndef INCLUDED_UHD_TYPES_SENSORS_H
#define INCLUDED_UHD_TYPES_SENSORS_H

#include <uhd/config.h>
#include <uhd/error.h>

#ifdef __cplusplus
#include <uhd/types/sensors.hpp>
#include <string>

struct uhd_sensor_value_t {
    // No default constructor, so we need a pointer
    uhd::sensor_value_t* sensor_value_cpp;
    std::string last_error;
};
extern "C" {
#else
struct uhd_sensor_value_t;
#endif

//! C-level interface for a UHD sensor
/*!
 * See uhd::sensor_value_t for more details.
 *
 * NOTE: Using a handle before calling a make function will result in undefined behavior.
 */
typedef struct uhd_sensor_value_t* uhd_sensor_value_handle;

//! Sensor value types
typedef enum {
    UHD_SENSOR_VALUE_BOOLEAN = 98,
    UHD_SENSOR_VALUE_INTEGER = 105,
    UHD_SENSOR_VALUE_REALNUM = 114,
    UHD_SENSOR_VALUE_STRING  = 115
} uhd_sensor_value_data_type_t;

//! Make a UHD sensor from a boolean.
/*!
 * \param h the sensor handle in which to place sensor
 * \param name sensor name
 * \param value sensor value
 * \param utrue string representing "true"
 * \param ufalse string representing "false"
 * \returns UHD error code
 */
UHD_API uhd_error uhd_sensor_value_make_from_bool(
    uhd_sensor_value_handle* h,
    const char* name,
    bool value,
    const char* utrue,
    const char* ufalse
);

//! Make a UHD sensor from an integer.
/*!
 * \param h the sensor value in which to place sensor
 * \param name sensor name
 * \param value sensor value
 * \param unit sensor unit
 * \param formatter printf-style format string for value string
 * \returns UHD error code
 */
UHD_API uhd_error uhd_sensor_value_make_from_int(
    uhd_sensor_value_handle* h,
    const char* name,
    int value,
    const char* unit,
    const char* formatter
);

//! Make a UHD sensor from a real number.
/*!
 * \param h the sensor value in which to place sensor
 * \param name sensor name
 * \param value sensor value
 * \param unit sensor unit
 * \param formatter printf-style format string for value string
 * \returns UHD error code
 */
UHD_API uhd_error uhd_sensor_value_make_from_realnum(
    uhd_sensor_value_handle* h,
    const char* name,
    double value,
    const char* unit,
    const char* formatter
);

//! Make a UHD sensor from a string.
/*!
 * \param h the sensor value in which to place sensor
 * \param name sensor name
 * \param value sensor value
 * \param unit sensor unit
 * \returns UHD error code
 */
UHD_API uhd_error uhd_sensor_value_make_from_string(
    uhd_sensor_value_handle* h,
    const char* name,
    const char* value,
    const char* unit
);

//! Free the given sensor handle.
/*!
 * Attempting to use the handle after calling this handle will
 * result in a segmentation fault.
 */
UHD_API uhd_error uhd_sensor_value_free(
    uhd_sensor_value_handle* h
);

//! Get the sensor's value as a boolean.
UHD_API uhd_error uhd_sensor_value_to_bool(
    uhd_sensor_value_handle h,
    bool *value_out
);

//! Get the sensor's value as an integer.
UHD_API uhd_error uhd_sensor_value_to_int(
    uhd_sensor_value_handle h,
    int *value_out
);

//! Get the sensor's value as a real number.
UHD_API uhd_error uhd_sensor_value_to_realnum(
    uhd_sensor_value_handle h,
    double *value_out
);

//! Get the sensor's name.
/*!
 * NOTE: This function will overwrite any string in the given
 * buffer before inserting the sensor name.
 *
 * \param h sensor handle
 * \param name_out string buffer in which to place name
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_sensor_value_name(
    uhd_sensor_value_handle h,
    char* name_out,
    size_t strbuffer_len
);

//! Get the sensor's value.
/*!
 * NOTE: This function will overwrite any string in the given
 * buffer before inserting the sensor value.
 *
 * \param h sensor handle
 * \param value_out string buffer in which to place value
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_sensor_value_value(
    uhd_sensor_value_handle h,
    char* value_out,
    size_t strbuffer_len
);

//! Get the sensor's unit.
/*!
 * NOTE: This function will overwrite any string in the given
 * buffer before inserting the sensor unit.
 *
 * \param h sensor handle
 * \param unit_out string buffer in which to place unit
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_sensor_value_unit(
    uhd_sensor_value_handle h,
    char* unit_out,
    size_t strbuffer_len
);

UHD_API uhd_error uhd_sensor_value_data_type(
    uhd_sensor_value_handle h,
    uhd_sensor_value_data_type_t *data_type_out
);

//! Get a pretty-print representation of the given sensor.
/*!
 * NOTE: This function will overwrite any string in the given
 * buffer before inserting the string.
 *
 * \param h sensor handle
 * \param pp_string_out string buffer in which to place pp_string
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_sensor_value_to_pp_string(
    uhd_sensor_value_handle h,
    char* pp_string_out,
    size_t strbuffer_len
);

//! Get the last error logged by the sensor handle.
/*!
 * NOTE: This function will overwrite any string in the given
 * buffer before inserting the error string.
 *
 * \param h sensor handle
 * \param error_out string buffer in which to place error
 * \param strbuffer_len buffer length
 */
UHD_API uhd_error uhd_sensor_value_last_error(
    uhd_sensor_value_handle h,
    char* error_out,
    size_t strbuffer_len
);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDED_UHD_TYPES_SENSORS_H */
