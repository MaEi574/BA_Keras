import keras
import hls4ml
from hls4ml.converters.keras_v3._base import KerasV3LayerHandler

class KCustomDSPDense(keras.layers.Dense):
    def __init__(self, units, **kwargs):
        super().__init__(units, **kwargs)
    
    def get_config(self):
        return super().get_config()
    
class HCustomDSPDense(hls4ml.model.layers.Dense):
    pass

class KCustomDSPDenseHandler(KerasV3LayerHandler):
    handles = ('KCustomDSPDense',)

    def handle(
        self,
        layer,
        in_tensors,
        out_tensors,
    ):
        kernel = self.load_weight(layer, 'kernel')
        bias = self.load_weight(layer, 'bias') if layer.use_bias else None
        n_in, n_out = kernel.shape  # type: ignore

        config = {
            'data_format': 'channels_last',
            'weight_data': kernel,
            'bias_data': bias,
            'n_out': n_out,
            'n_in': n_in,
        }
        return config