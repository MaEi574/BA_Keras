from hls4ml.backends.backend import get_backend
from hls4ml.backends.template import FunctionCallTemplate, LayerConfigTemplate
import custom

# Regular dense config template
custom_dsp_dense_config_template = """struct config{index} : nnet::dense_config {{
    static const unsigned n_in = {n_in};
    static const unsigned n_out = {n_out};
    static const unsigned io_type = nnet::{iotype};
    static const unsigned strategy = nnet::{strategy};
    static const unsigned reuse_factor = {reuse};
    static const unsigned n_zeros = {nzeros};
    static const unsigned n_nonzeros = {nonzeros};
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in * n_out, reuse_factor) - n_zeros / reuse_factor;
    static const bool store_weights_in_bram = false;
    typedef {accum_t.name} accum_t;
    typedef {bias_t.name} bias_t;
    typedef {weight_t.name} weight_t;
    typedef {index_t.name} index_t;
    template<class data_T, class res_T, class CONFIG_T>
    using kernel = {dense_function}<data_T, res_T, CONFIG_T>;
    template<class x_T, class y_T>
    using product = nnet::product::{product_type}<x_T, y_T>;
}};\n"""

# Regular dense function template
custom_dsp_dense_function_template = 'nnet::dense<{input_t}, {output_t}, {config}>({input}, {output}, {w}, {b});'

custom_dsp_dense_include_list = ['nnet_utils/nnet_dense.h', 'nnet_utils/nnet_custom_dsp_dense.h']

class CustomDSPDenseConfigTemplate(LayerConfigTemplate):
    def __init__(self):
        super().__init__(custom.HCustomDSPDense)
        self.template = custom_dsp_dense_config_template

    def format(self, node):
        params = self._default_config_params(node)
        params['nzeros'] = node.get_weights('weight').nzeros
        params['nonzeros'] = node.get_weights('weight').nonzeros
        params['product_type'] = get_backend('vivado').product_type(
            node.get_input_variable().type.precision, node.get_weights('weight').type.precision
        )

        if node.get_attr('strategy').lower() == 'resource':
            if int(params['reuse_factor']) == int(params['n_in']):
                params['dense_function'] = 'nnet::Custom_dsp_dense'
            else:
                raise ValueError("CustomDSPDense requires ReuseFactor == n_in!")
        else:
            raise ValueError("CustomDSPDense requires strategy == 'resource'!")

        return self.template.format(**params)

    def match(self, node):
        return super().match(node)


class CustomDSPDenseFunctionTemplate(FunctionCallTemplate):
    def __init__(self):
        super().__init__(custom.HCustomDSPDense, include_header=custom_dsp_dense_include_list)
        self.template = custom_dsp_dense_function_template

    def format(self, node):
        params = self._default_function_params(node)
        params['w'] = node.get_weights('weight').name
        params['b'] = node.get_weights('bias').name

        return self.template.format(**params)

    def match(self, node):
        return super().match(node)