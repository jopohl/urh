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

#ifndef INCLUDED_UHD_TYPES_RANGES_H
#define INCLUDED_UHD_TYPES_RANGES_H

#include <uhd/config.h>
#include <uhd/error.h>

#include <stdbool.h>
#include <stdlib.h>

//! Range of floating-point values
typedef struct {
    //! First value
    double start;
    //! Last value
    double stop;
    //! Granularity
    double step;
} uhd_range_t;

#ifdef __cplusplus
#include <uhd/types/ranges.hpp>
#include <string>

struct uhd_meta_range_t {
    uhd::meta_range_t meta_range_cpp;
    std::string last_error;
};

extern "C" {
#else
struct uhd_meta_range_t;
#endif

//! C-level interface for dealing with a list of ranges
/*!
 * See uhd::meta_range_t for more details.
 */
typedef struct uhd_meta_range_t* uhd_meta_range_handle;

//! Get a string representation of the given range
UHD_API uhd_error uhd_range_to_pp_string(
    const uhd_range_t *range,
    char* pp_string_out,
    size_t strbuffer_len
);

//! Create a meta range handle
/*!
 * NOTE: Using a uhd_meta_range_handle before passing it into this function will
 * result in undefined behavior.
 */
UHD_API uhd_error uhd_meta_range_make(
    uhd_meta_range_handle* h
);

//! Destroy a meta range handle
/*!
 * NOTE: Using a uhd_meta_range_handle after passing it into this function will
 * result in a segmentation fault.
 */
UHD_API uhd_error uhd_meta_range_free(
    uhd_meta_range_handle* h
);

//! Get the overall start value for the given meta range
UHD_API uhd_error uhd_meta_range_start(
    uhd_meta_range_handle h,
    double *start_out
);

//! Get the overall stop value for the given meta range
UHD_API uhd_error uhd_meta_range_stop(
    uhd_meta_range_handle h,
    double *stop_out
);

//! Get the overall step value for the given meta range
UHD_API uhd_error uhd_meta_range_step(
    uhd_meta_range_handle h,
    double *step_out
);

//! Clip the given value to a possible value in the given range
UHD_API uhd_error uhd_meta_range_clip(
    uhd_meta_range_handle h,
    double value,
    bool clip_step,
    double *result_out
);

//! Get the number of ranges in the given meta range
UHD_API uhd_error uhd_meta_range_size(
    uhd_meta_range_handle h,
    size_t *size_out
);

//! Add a range to the given meta range
UHD_API uhd_error uhd_meta_range_push_back(
    uhd_meta_range_handle h,
    const uhd_range_t *range
);

//! Get the range at the given index
UHD_API uhd_error uhd_meta_range_at(
    uhd_meta_range_handle h,
    size_t num,
    uhd_range_t *range_out
);

//! Get a string representation of the given meta range
UHD_API uhd_error uhd_meta_range_to_pp_string(
    uhd_meta_range_handle h,
    char* pp_string_out,
    size_t strbuffer_len
);

//! Get the last error recorded by the underlying meta range
UHD_API uhd_error uhd_meta_range_last_error(
    uhd_meta_range_handle h,
    char* error_out,
    size_t strbuffer_len
);

#ifdef __cplusplus
}

UHD_API uhd::range_t uhd_range_c_to_cpp(
    const uhd_range_t *range_c
);

UHD_API void uhd_range_cpp_to_c(
    const uhd::range_t &range_cpp,
    uhd_range_t *range_c
);
#endif

#endif /* INCLUDED_UHD_TYPES_RANGES_H */
