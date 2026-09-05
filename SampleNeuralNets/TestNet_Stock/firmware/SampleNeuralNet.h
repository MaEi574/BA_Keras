#ifndef SAMPLENEURALNET_H_
#define SAMPLENEURALNET_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "hls_stream.h"

#include "defines.h"


// Prototype of top level function for C-synthesis
void SampleNeuralNet(
    input_t input_layer[8],
    result_t layer5_out[1]
);

// hls-fpga-machine-learning insert emulator-defines


#endif
