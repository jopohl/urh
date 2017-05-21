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

#ifndef INCLUDED_UHD_USRP_SUBDEV_SPEC_H
#define INCLUDED_UHD_USRP_SUBDEV_SPEC_H

#include <uhd/config.h>
#include <uhd/error.h>

#include <stdbool.h>

//! Subdevice specification
typedef struct {
    // Daughterboard slot name
    char* db_name;
    //! Subdevice name
    char* sd_name;
} uhd_subdev_spec_pair_t;

#ifdef __cplusplus
#include <uhd/usrp/subdev_spec.hpp>
#include <string>

struct uhd_subdev_spec_t {
    uhd::usrp::subdev_spec_t subdev_spec_cpp;
    std::string last_error;
};

extern "C" {
#else
struct uhd_subdev_spec_t;
#endif

//! A C-level interface for working with a list of subdevice specifications
/*!
 * See uhd::usrp::subdev_spec_t for more details.
 *
 * NOTE: Using a handle before passing it into uhd_subdev_spec_make() will result in
 * undefined behavior.
 */
typedef struct uhd_subdev_spec_t* uhd_subdev_spec_handle;

//! Safely destroy any memory created in the generation of a uhd_subdev_spec_pair_t
UHD_API uhd_error uhd_subdev_spec_pair_free(
    uhd_subdev_spec_pair_t *subdev_spec_pair
);

//! Check to see if two subdevice specifications are equal
UHD_API uhd_error uhd_subdev_spec_pairs_equal(
    const uhd_subdev_spec_pair_t* first,
    const uhd_subdev_spec_pair_t* second,
    bool *result_out
);

//! Create a handle for a list of subdevice specifications
UHD_API uhd_error uhd_subdev_spec_make(
    uhd_subdev_spec_handle* h,
    const char* markup
);

//! Safely destroy a subdevice specification handle
/*!
 * NOTE: Using a handle after passing it into this function will result in
 * a segmentation fault.
 */
UHD_API uhd_error uhd_subdev_spec_free(
    uhd_subdev_spec_handle* h
);

//! Check how many subdevice specifications are in this list
UHD_API uhd_error uhd_subdev_spec_size(
    uhd_subdev_spec_handle h,
    size_t *size_out
);

//! Add a subdevice specification to this list
UHD_API uhd_error uhd_subdev_spec_push_back(
    uhd_subdev_spec_handle h,
    const char* markup
);

//! Get the subdevice specification at the given index
UHD_API uhd_error uhd_subdev_spec_at(
    uhd_subdev_spec_handle h,
    size_t num,
    uhd_subdev_spec_pair_t *subdev_spec_pair_out
);

//! Get a string representation of the given list
UHD_API uhd_error uhd_subdev_spec_to_pp_string(
    uhd_subdev_spec_handle h,
    char* pp_string_out,
    size_t strbuffer_len
);

//! Get a markup string representation of the given list
UHD_API uhd_error uhd_subdev_spec_to_string(
    uhd_subdev_spec_handle h,
    char* string_out,
    size_t strbuffer_len
);

//! Get the last error recorded by the given handle
UHD_API uhd_error uhd_subdev_spec_last_error(
    uhd_subdev_spec_handle h,
    char* error_out,
    size_t strbuffer_len
);

#ifdef __cplusplus
}

UHD_API uhd::usrp::subdev_spec_pair_t uhd_subdev_spec_pair_c_to_cpp(
    const uhd_subdev_spec_pair_t* subdev_spec_pair_c
);

UHD_API void uhd_subdev_spec_pair_cpp_to_c(
    const uhd::usrp::subdev_spec_pair_t &subdev_spec_pair_cpp,
    uhd_subdev_spec_pair_t *subdev_spec_pair_c
);
#endif

#endif /* INCLUDED_UHD_USRP_SUBDEV_SPEC_H */
