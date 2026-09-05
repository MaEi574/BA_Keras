#ifndef NNET_CUSTOM_DSP_DENSE_H_
#define NNET_CUSTOM_DSP_DENSE_H_

#include "nnet_dense.h"
#include "nnet_custom_dsp_dense_implementation.h"

namespace nnet {
    
    template <class data_T, class res_T, typename CONFIG_T>
    class Custom_dsp_dense : public DenseKernel<data_T, res_T, CONFIG_T> {
    public:
        static void dense(data_T data[CONFIG_T::n_in], res_T res[CONFIG_T::n_out],
                        typename CONFIG_T::weight_t weights[CONFIG_T::n_in * CONFIG_T::n_out],
                        typename CONFIG_T::bias_t biases[CONFIG_T::n_out]) {
            #pragma HLS INLINE
            custom_dsp_dense_implementation<data_T, res_T, CONFIG_T>(data, res, weights, biases);
        }
    };

}

#endif
