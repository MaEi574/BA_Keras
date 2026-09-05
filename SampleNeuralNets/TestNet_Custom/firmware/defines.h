#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <array>
#include <cstddef>
#include <cstdio>
#include <tuple>
#include <tuple>


// hls-fpga-machine-learning insert numbers

// hls-fpga-machine-learning insert layer-precision
typedef ap_int<16> input_t;
typedef ap_int<48> dense1_accum_t;
typedef ap_int<48> layer2_t;
typedef ap_int<16> dense1_weight_t;
typedef ap_int<16> dense1_bias_t;
typedef ap_uint<1> layer2_index;
typedef ap_int<16> layer3_t;
typedef ap_int<48> relu1_param_t;
typedef ap_fixed<18,8> relu1_table_t;
typedef ap_int<48> dense2_accum_t;
typedef ap_int<48> layer4_t;
typedef ap_int<16> dense2_weight_t;
typedef ap_int<16> dense2_bias_t;
typedef ap_uint<1> layer4_index;
typedef ap_int<16> result_t;
typedef ap_int<48> relu2_param_t;
typedef ap_fixed<18,8> relu2_table_t;

// hls-fpga-machine-learning insert emulator-defines


#endif
