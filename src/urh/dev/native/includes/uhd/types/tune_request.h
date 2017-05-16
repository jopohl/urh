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

#ifndef INCLUDED_UHD_TYPES_TUNE_REQUEST_H
#define INCLUDED_UHD_TYPES_TUNE_REQUEST_H

#include <uhd/config.h>

#include <stdlib.h>

//! Policy options for tunable elements in the RF chain.
typedef enum {
    //! Do not set this argument, use current setting.
    UHD_TUNE_REQUEST_POLICY_NONE   = 78,
    //! Automatically determine the argument's value.
    UHD_TUNE_REQUEST_POLICY_AUTO   = 65,
    //! Use the argument's value for the setting.
    UHD_TUNE_REQUEST_POLICY_MANUAL = 77
} uhd_tune_request_policy_t;

//! Instructs implementation how to tune the RF chain
/*!
 * See uhd::tune_request_t for more details.
 */
typedef struct {
    //! Target frequency for RF chain in Hz
    double target_freq;
    //! RF frequency policy
    uhd_tune_request_policy_t rf_freq_policy;
    //! RF frequency in Hz
    double rf_freq;
    //! DSP frequency policy
    uhd_tune_request_policy_t dsp_freq_policy;
    //! DSP frequency in Hz
    double dsp_freq;
    //! Key-value pairs delimited by commas
    char* args;
} uhd_tune_request_t;

#ifdef __cplusplus
#include <uhd/types/tune_request.hpp>

UHD_API uhd::tune_request_t uhd_tune_request_c_to_cpp(uhd_tune_request_t *tune_request_c);

#endif

#endif /* INCLUDED_UHD_TYPES_TUNE_REQUEST_H */
