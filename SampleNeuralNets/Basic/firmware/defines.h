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
typedef ap_fixed<16,6> input_t;
typedef ap_fixed<36,16> dense1_accum_t;
typedef ap_fixed<36,16> dense1_result_t;
typedef ap_fixed<16,6> dense1_weight_t;
typedef ap_fixed<16,6> dense1_bias_t;
typedef ap_uint<1> layer2_index;
typedef ap_fixed<16,6> layer3_t;
typedef ap_fixed<36,16> relu1_param_t;
typedef ap_fixed<18,8> relu1_table_t;
typedef ap_fixed<36,16> dense2_accum_t;
typedef ap_fixed<36,16> dense2_result_t;
typedef ap_fixed<16,6> dense2_weight_t;
typedef ap_fixed<16,6> dense2_bias_t;
typedef ap_uint<1> layer4_index;
typedef ap_fixed<16,6> layer5_t;
typedef ap_fixed<36,16> relu2_param_t;
typedef ap_fixed<18,8> relu2_table_t;
typedef ap_fixed<36,16> dense3_accum_t;
typedef ap_fixed<36,16> dense3_result_t;
typedef ap_fixed<16,6> dense3_weight_t;
typedef ap_fixed<16,6> dense3_bias_t;
typedef ap_uint<1> layer6_index;
typedef ap_fixed<16,6> result_t;
typedef ap_fixed<36,16> relu3_param_t;
typedef ap_fixed<18,8> relu3_table_t;

// hls-fpga-machine-learning insert emulator-defines


#endif
