#ifndef NNET_CUSTOM_DSP_DENSE_IMPLEMENTATION_H_
#define NNET_CUSTOM_DSP_DENSE_IMPLEMENTATION_H_

#include "nnet_common.h"
#include "nnet_mult.h"
#include <assert.h>
#include <math.h>

#include "hls_dsp_builtins.h"

typedef hls::dsp48e1::acc<
    hls::dsp::REG_A1 |
    hls::dsp::REG_A2 |
    hls::dsp::REG_B1 |
    hls::dsp::REG_B2 |
    hls::dsp::REG_M |
    hls::dsp::REG_P
> dsp_acc_t;

namespace nnet {
    
    template <class data_T, class res_T, typename CONFIG_T>
    void custom_dsp_dense_implementation(data_T data[CONFIG_T::n_in], res_T res[CONFIG_T::n_out],
                                typename CONFIG_T::weight_t weights[CONFIG_T::n_in * CONFIG_T::n_out],
                                typename CONFIG_T::bias_t biases[CONFIG_T::n_out]) {

        const int rufactor = CONFIG_T::reuse_factor;                                                    // ALWAYS 8 HERE
        const int multfactor = MIN(CONFIG_T::n_in, CONFIG_T::reuse_factor);                             // ALWAYS 8 HERE           
        const int multiplier_limit = DIV_ROUNDUP(CONFIG_T::n_in * CONFIG_T::n_out, multfactor);         // ALWAYS 8 HERE
        const int block_factor = DIV_ROUNDUP(CONFIG_T::n_in * CONFIG_T::n_out, CONFIG_T::reuse_factor); // ALWAYS 8 HERE
        const int nin = CONFIG_T::n_in;                                                                 // ALWAYS 8 HERE
        const int nout = CONFIG_T::n_out;                                                               // ALWAYS 8 HERE

        assert((multiplier_limit % nout == 0 || rufactor >= nin) && "The current Reuse Factor is not allowed");
        assert((multiplier_limit == block_factor) && "This function is correct only for RF <= N_IN");

        #pragma HLS function_instantiate variable=weights,biases
        #pragma HLS ARRAY_RESHAPE   variable=weights block factor=block_factor
        #pragma HLS ARRAY_PARTITION variable=biases complete

        if (CONFIG_T::reuse_factor > 1) {
            #pragma HLS RESOURCE variable=weights core=ROM_nP_BRAM
        }

        // typename CONFIG_T::accum_t runningSumArray[CONFIG_T::n_out];
        // #pragma HLS ARRAY_PARTITION variable=runningSumArray complete

        dsp_acc_t dspAccumulators[CONFIG_T::n_out];
        #pragma HLS ARRAY_PARTITION variable=dspAccumulators complete

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // RUFACTOR IS ALWAYS 8 HERE

    InputLoop:
        for (int inputLoopIndex = 0; inputLoopIndex < rufactor+1; inputLoopIndex++) {      // Loop through all inputs -> inputLoopIndex = x <-> working on input x
            #pragma HLS PIPELINE II=1 rewind


        NeuronLoop:
            for (int neuronLoopIndex = 0; neuronLoopIndex < block_factor; neuronLoopIndex++) {       // Loop through all neurons -> neuronLoopIndex = y <-> input_x * weight_y_x
                #pragma HLS UNROLL

                hls::dsp48e1::A_t dspA;
                hls::dsp48e1::B_t dspB;
                bool dspInit;
                int weightSelectIndex;
                int inputSelectIndex;

                if (inputLoopIndex == 0) {  // EXECUTE FOR THE FIRST LOOP ITERATION: INITIALIZE ACCUMULATOR REGISTERS WITH BIASES
                    dspA = (hls::dsp48e1::A_t)biases[neuronLoopIndex];
                    dspB = (hls::dsp48e1::B_t)1;
                    dspInit = true;
                }
                else {                      // EXECUTE FOR REMAINING 8 LOOP ITERATIONS: REGULAR input_x * weight_y_x MAC
                    weightSelectIndex = inputLoopIndex-1;
                    inputSelectIndex = inputLoopIndex-1;
                    dspA = (hls::dsp48e1::A_t)data[inputSelectIndex];
                    dspB = (hls::dsp48e1::B_t)weights[weightSelectIndex];
                    dspInit = false;

                    // Increment weightSelectIndex
                    weightSelectIndex += rufactor;    // ADDING 8 TO THE WEIGHTS INDEX GIVES US THE NEXT NEURON'S WEIGHT FOR THAT INPUT, e.g:
                                                    // weights[0] = w_0_0 (neuron 0, input 0), weights[8] = w_1_0 (neuron 1, input 0)
                    }

                dspAccumulators[neuronLoopIndex].mul_acc(dspA, dspB, dspInit);

            }
        }

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Cast to "res_t" type
    Result:
        for (int resultLoopIndex = 0; resultLoopIndex < CONFIG_T::n_out; resultLoopIndex++) {
            #pragma HLS UNROLL

            typename CONFIG_T::accum_t dspOutputSum = (typename CONFIG_T::accum_t) dspAccumulators[resultLoopIndex].get_accumulator();

            res[resultLoopIndex] = cast<data_T, res_T, CONFIG_T>(dspOutputSum);
        }
    }

}

#endif