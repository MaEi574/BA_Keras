#include <iostream>

#include "SampleNeuralNet.h"
#include "parameters.h"


void SampleNeuralNet(
    input_t input_layer[8],
    result_t layer5_out[1]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS ARRAY_RESHAPE variable=input_layer complete dim=0
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0
    #pragma HLS INTERFACE ap_vld port=input_layer,layer5_out 
    #pragma HLS DATAFLOW

    // hls-fpga-machine-learning insert load weights
#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        nnet::load_weights_from_txt<dense1_weight_t, 16>(w2, "w2.txt");
        nnet::load_weights_from_txt<dense1_bias_t, 2>(b2, "b2.txt");
        nnet::load_weights_from_txt<dense2_weight_t, 2>(w4, "w4.txt");
        nnet::load_weights_from_txt<dense2_bias_t, 1>(b4, "b4.txt");
        loaded_weights = true;    }
#endif
    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[2];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0

    layer3_t layer3_out[2];
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0

    layer4_t layer4_out[1];
    #pragma HLS ARRAY_PARTITION variable=layer4_out complete dim=0

    nnet::dense<input_t, layer2_t, config2>(input_layer, layer2_out, w2, b2); // dense1

    nnet::thresholded_relu<layer2_t, relu1_param_t, layer3_t, thresholdedrelu_config3>(layer2_out, 0.0, layer3_out); // relu1

    nnet::dense<layer3_t, layer4_t, config4>(layer3_out, layer4_out, w4, b4); // dense2

    nnet::thresholded_relu<layer4_t, relu2_param_t, result_t, thresholdedrelu_config5>(layer4_out, 0.0, layer5_out); // relu2

}

