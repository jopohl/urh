/* -*- c++ -*- */
/*
 * Copyright 2006,2010-2012 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "costas_loop_cc_impl.h"
#include <gnuradio/io_signature.h>
#include <gnuradio/expj.h>
#include <gnuradio/sincos.h>
#include <gnuradio/math.h>
#include <boost/format.hpp>

namespace gr {
  namespace digital {

    costas_loop_cc::sptr
    costas_loop_cc::make(float loop_bw, int order, bool use_snr)
    {
      return gnuradio::get_initial_sptr
	(new costas_loop_cc_impl(loop_bw, order, use_snr));
    }

    costas_loop_cc_impl::costas_loop_cc_impl(float loop_bw, int order, bool use_snr)
      : sync_block("costas_loop_cc",
                   io_signature::make(1, 1, sizeof(gr_complex)),
                   io_signature::make2(1, 2, sizeof(gr_complex), sizeof(float))),
	blocks::control_loop(loop_bw, 1.0, -1.0),
	d_order(order), d_error(0), d_noise(1.0), d_phase_detector(NULL)
    {
      // Set up the phase detector to use based on the constellation order
      switch(d_order) {
      case 2:
        if(use_snr)
          d_phase_detector = &costas_loop_cc_impl::phase_detector_snr_2;
	else
          d_phase_detector = &costas_loop_cc_impl::phase_detector_2;
	break;

      case 4:
        if(use_snr)
          d_phase_detector = &costas_loop_cc_impl::phase_detector_snr_4;
	else
          d_phase_detector = &costas_loop_cc_impl::phase_detector_4;
	break;

      case 8:
        if(use_snr)
          d_phase_detector = &costas_loop_cc_impl::phase_detector_snr_8;
	else
          d_phase_detector = &costas_loop_cc_impl::phase_detector_8;
	break;

      default:
	throw std::invalid_argument("order must be 2, 4, or 8");
	break;
      }

      message_port_register_in(pmt::mp("noise"));
      set_msg_handler(
        pmt::mp("noise"),
        boost::bind(&costas_loop_cc_impl::handle_set_noise,
                    this, _1));
    }

    costas_loop_cc_impl::~costas_loop_cc_impl()
    {
    }

    float
    costas_loop_cc_impl::phase_detector_8(gr_complex sample) const
    {
      /* This technique splits the 8PSK constellation into 2 squashed
	 QPSK constellations, one when I is larger than Q and one
	 where Q is larger than I. The error is then calculated
	 proportionally to these squashed constellations by the const
	 K = sqrt(2)-1.

	 The signal magnitude must be > 1 or K will incorrectly bias
	 the error value.

	 Ref: Z. Huang, Z. Yi, M. Zhang, K. Wang, "8PSK demodulation for
	 new generation DVB-S2", IEEE Proc. Int. Conf. Communications,
	 Circuits and Systems, Vol. 2, pp. 1447 - 1450, 2004.
      */

      float K = (sqrt(2.0) - 1);
      if(fabsf(sample.real()) >= fabsf(sample.imag())) {
	return ((sample.real()>0 ? 1.0 : -1.0) * sample.imag() -
		(sample.imag()>0 ? 1.0 : -1.0) * sample.real() * K);
      }
      else {
	return ((sample.real()>0 ? 1.0 : -1.0) * sample.imag() * K -
		(sample.imag()>0 ? 1.0 : -1.0) * sample.real());
      }
    }

    float
    costas_loop_cc_impl::phase_detector_4(gr_complex sample) const
    {
      return ((sample.real()>0 ? 1.0 : -1.0) * sample.imag() -
	      (sample.imag()>0 ? 1.0 : -1.0) * sample.real());
    }

    float
    costas_loop_cc_impl::phase_detector_2(gr_complex sample) const
    {
      return (sample.real()*sample.imag());
    }

    float
    costas_loop_cc_impl::phase_detector_snr_8(gr_complex sample) const
    {
      float K = (sqrt(2.0) - 1);
      float snr = abs(sample)*abs(sample) / d_noise;
      if(fabsf(sample.real()) >= fabsf(sample.imag())) {
	return ((blocks::tanhf_lut(snr*sample.real()) * sample.imag()) -
          (blocks::tanhf_lut(snr*sample.imag()) * sample.real() * K));
      }
      else {
	return ((blocks::tanhf_lut(snr*sample.real()) * sample.imag() * K) -
          (blocks::tanhf_lut(snr*sample.imag()) * sample.real()));
      }
    }

    float
    costas_loop_cc_impl::phase_detector_snr_4(gr_complex sample) const
    {
      float snr = abs(sample)*abs(sample) / d_noise;
      return ((blocks::tanhf_lut(snr*sample.real()) * sample.imag()) -
              (blocks::tanhf_lut(snr*sample.imag()) * sample.real()));
    }

    float
    costas_loop_cc_impl::phase_detector_snr_2(gr_complex sample) const
    {
      float snr = abs(sample)*abs(sample) / d_noise;
      return blocks::tanhf_lut(snr*sample.real()) * sample.imag();
    }

    float
    costas_loop_cc_impl::error() const
    {
      return d_error;
    }

    void
    costas_loop_cc_impl::handle_set_noise(pmt::pmt_t msg)
    {
      if(pmt::is_real(msg)) {
        d_noise = pmt::to_double(msg);
        d_noise = powf(10.0f, d_noise/10.0f);
      }
    }

    int
    costas_loop_cc_impl::work(int noutput_items,
			      gr_vector_const_void_star &input_items,
			      gr_vector_void_star &output_items)
    {
      const gr_complex *iptr = (gr_complex *) input_items[0];
      gr_complex *optr = (gr_complex *) output_items[0];
      float *foptr = (float *) output_items[1];

      bool write_foptr = output_items.size() >= 2;

      gr_complex nco_out;

      std::vector<tag_t> tags;
      get_tags_in_range(tags, 0, nitems_read(0),
                        nitems_read(0)+noutput_items,
                        pmt::intern("phase_est"));

      if(write_foptr) {
        for(int i = 0; i < noutput_items; i++) {
          if(tags.size() > 0) {
            if(tags[0].offset-nitems_read(0) == (size_t)i) {
              d_phase = (float)pmt::to_double(tags[0].value);
              tags.erase(tags.begin());
            }
          }

          nco_out = gr_expj(-d_phase);
          optr[i] = iptr[i] * nco_out;

          d_error = (*this.*d_phase_detector)(optr[i]);
          d_error = gr::branchless_clip(d_error, 1.0);

          advance_loop(d_error);
          phase_wrap();
          frequency_limit();

          foptr[i] = d_freq;
        }
      }
      else {
        for(int i = 0; i < noutput_items; i++) {
          if(tags.size() > 0) {
            if(tags[0].offset-nitems_read(0) == (size_t)i) {
              d_phase = (float)pmt::to_double(tags[0].value);
              tags.erase(tags.begin());
            }
          }

          nco_out = gr_expj(-d_phase);
          optr[i] = iptr[i] * nco_out;

          d_error = (*this.*d_phase_detector)(optr[i]);
          d_error = gr::branchless_clip(d_error, 1.0);

          advance_loop(d_error);
          phase_wrap();
          frequency_limit();
        }
      }

      return noutput_items;
    }

    void
    costas_loop_cc_impl::setup_rpc()
    {
#ifdef GR_CTRLPORT
      // Getters
      add_rpc_variable(
          rpcbasic_sptr(new rpcbasic_register_get<costas_loop_cc, float>(
	      alias(), "error",
	      &costas_loop_cc::error,
	      pmt::mp(-2.0f), pmt::mp(2.0f), pmt::mp(0.0f),
	      "", "Error signal of loop", RPC_PRIVLVL_MIN,
              DISPTIME | DISPOPTSTRIP)));

      add_rpc_variable(
          rpcbasic_sptr(new rpcbasic_register_get<control_loop, float>(
	      alias(), "frequency",
	      &control_loop::get_frequency,
	      pmt::mp(0.0f), pmt::mp(2.0f), pmt::mp(0.0f),
	      "", "Frequency Est.", RPC_PRIVLVL_MIN,
              DISPTIME | DISPOPTSTRIP)));

      add_rpc_variable(
          rpcbasic_sptr(new rpcbasic_register_get<control_loop, float>(
	      alias(), "phase",
	      &control_loop::get_phase,
	      pmt::mp(0.0f), pmt::mp(2.0f), pmt::mp(0.0f),
	      "", "Phase Est.", RPC_PRIVLVL_MIN,
              DISPTIME | DISPOPTSTRIP)));

      add_rpc_variable(
          rpcbasic_sptr(new rpcbasic_register_get<control_loop, float>(
	      alias(), "loop_bw",
	      &control_loop::get_loop_bandwidth,
	      pmt::mp(0.0f), pmt::mp(2.0f), pmt::mp(0.0f),
	      "", "Loop bandwidth", RPC_PRIVLVL_MIN,
              DISPTIME | DISPOPTSTRIP)));

      // Setters
      add_rpc_variable(
          rpcbasic_sptr(new rpcbasic_register_set<control_loop, float>(
	      alias(), "loop bw",
	      &control_loop::set_loop_bandwidth,
	      pmt::mp(0.0f), pmt::mp(1.0f), pmt::mp(0.0f),
	      "", "Loop bandwidth",
	      RPC_PRIVLVL_MIN, DISPNULL)));
#endif /* GR_CTRLPORT */
    }

  } /* namespace digital */
} /* namespace gr */
