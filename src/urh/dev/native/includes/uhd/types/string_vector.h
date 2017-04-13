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

#ifndef INCLUDED_UHD_TYPES_STRING_VECTOR_H
#define INCLUDED_UHD_TYPES_STRING_VECTOR_H

#include <uhd/config.h>
#include <uhd/error.h>

#include <stdlib.h>

#ifdef __cplusplus
#include <string>
#include <vector>

struct uhd_string_vector_t {
    std::vector<std::string> string_vector_cpp;
    std::string last_error;
};

extern "C" {
#else
//! C-level read-only interface for interacting with a string vector
struct uhd_string_vector_t;
#endif

typedef struct uhd_string_vector_t uhd_string_vector_t;

typedef uhd_string_vector_t* uhd_string_vector_handle;

//! Instantiate a string_vector handle.
UHD_API uhd_error uhd_string_vector_make(
    uhd_string_vector_handle *h
);

//! Safely destroy a string_vector handle.
UHD_API uhd_error uhd_string_vector_free(
    uhd_string_vector_handle *h
);

//! Add a string to the list
UHD_API uhd_error uhd_string_vector_push_back(
    uhd_string_vector_handle *h,
    const char* value
);

//! Get the string at the given index
UHD_API uhd_error uhd_string_vector_at(
    uhd_string_vector_handle h,
    size_t index,
    char* value_out,
    size_t strbuffer_len
);

//! Get the number of strings in this list
UHD_API uhd_error uhd_string_vector_size(
    uhd_string_vector_handle h,
    size_t *size_out
);

//! Get the last error reported by the underlying object
UHD_API uhd_error uhd_string_vector_last_error(
    uhd_string_vector_handle h,
    char* error_out,
    size_t strbuffer_len
);

#ifdef __cplusplus
}
#endif

#endif /* INCLUDED_UHD_TYPES_STRING_VECTOR_H */
