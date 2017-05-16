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

#ifndef INCLUDED_UHD_TYPES_TUNE_RESULT_H
#define INCLUDED_UHD_TYPES_TUNE_RESULT_H

#include <uhd/config.h>

#include <stdlib.h>

//! Stores RF and DSP tuned frequencies.
/*!
 * See uhd::tune_result_t for more details.
 */
typedef struct {
    //! Target RF frequency, clipped to be within system range
    double clipped_rf_freq;
    //! Target RF frequency, including RF FE offset
    double target_rf_freq;
    //! Frequency to which RF LO is actually tuned
    double actual_rf_freq;
    //! Frequency the CORDIC must adjust the RF
    double target_dsp_freq;
    //! Frequency to which the CORDIC in the DSP actually tuned
    double actual_dsp_freq;
} uhd_tune_result_t;

#ifdef __cplusplus
extern "C" {
#endif

//! Create a pretty print representation of this tune result.
UHD_API void uhd_tune_result_to_pp_string(uhd_tune_result_t *tune_result,
                                          char* pp_string_out, size_t strbuffer_len);

#ifdef __cplusplus
}
#include <uhd/types/tune_result.hpp>

UHD_API uhd::tune_result_t uhd_tune_result_c_to_cpp(uhd_tune_result_t *tune_result_c);

UHD_API void uhd_tune_result_cpp_to_c(const uhd::tune_result_t &tune_result_cpp,
                                      uhd_tune_result_t *tune_result_c);
#endif

#endif /* INCLUDED_UHD_TYPES_TUNE_RESULT_H */
