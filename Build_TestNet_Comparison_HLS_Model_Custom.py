import keras
import hls4ml

import numpy as np
import os
import json
import pathlib
import custom
import templates

### REGISTRATIONS

# Register the hls4ml's IR layer
hls4ml.model.layers.register_layer('KCustomDSPDense', custom.HCustomDSPDense)

# Register the optimization passes (if any)
backend = hls4ml.backends.get_backend("Vitis")

# Register template passes for the given backend
backend.register_template(templates.CustomDSPDenseConfigTemplate)
backend.register_template(templates.CustomDSPDenseFunctionTemplate)

# Register HLS implementation
backend.register_source(str(pathlib.Path('./nnet_custom_dsp_dense.h').resolve()))
backend.register_source(str(pathlib.Path('./nnet_custom_dsp_dense_implementation.h').resolve()))

### Keras definition and initalization of neural network

os.makedirs("./SampleNeuralNets", exist_ok = True)

weights1 = np.array([
    [2,     -1],
    [2,     -5],
    [2,     7],
    [2,     91],
    [2,     3],
    [2,     -4],
    [0,     -7],
    [2,     3]
])

weights2 = np.array([
    [1],
    [2]
])

bias1 = np.array([2, 2])

bias2 = np.array([2])

model = keras.Sequential([
    keras.Input(shape = (8,)),
    
    custom.KCustomDSPDense(2, activation = None, name = "dense1"),
    keras.layers.ReLU(name = "relu1"),
    custom.KCustomDSPDense(1, activation = None, name = "dense2"),
    keras.layers.ReLU(name = "relu2"),
])

model.get_layer("dense1").set_weights([weights1, bias1])
model.get_layer("dense2").set_weights([weights2, bias2])

model.summary()
    
### hls4ml conversion
config = hls4ml.utils.config_from_keras_model(
    model,
    granularity = "name",
    backend = "Vitis",
    default_precision = "int<16>",
    default_reuse_factor = 8,
)

for denseName in ["dense1", "dense2"]:

    config["LayerName"][denseName]["Precision"]["weight"] = "int<16>"
    config["LayerName"][denseName]["Precision"]["bias"] = "int<16>"
    config["LayerName"][denseName]["Precision"]["accum"] = "int<48>"
    config["LayerName"][denseName]["Precision"]["result"] = "int<48>"
    
    if (denseName == "dense1"):
        reuseFactor = 8
    else:
        reuseFactor = 2
    config["LayerName"][denseName]["ReuseFactor"] = reuseFactor
    config["LayerName"][denseName]["Strategy"] = "Resource"
    
for reluName in ["relu1", "relu2"]:
    config["LayerName"][reluName]["Precision"]["result"] = "int<16>"
    config["LayerName"][reluName]["Strategy"] = "Resource"
    
config["LayerName"]["input_layer"]["Precision"]["result"] = "int<16>"

with open("Vitis_HLS_Config.json", "w") as f:
    json.dump(config, f, indent = 2)
    
BUILD_NAME = "TestNet_Custom"
BUILD_PATH = "./SampleNeuralNets/" + BUILD_NAME
os.makedirs(BUILD_PATH, exist_ok = True)
    
vitisModel = hls4ml.converters.convert_from_keras_model(
    model,
    hls_config = config,
    project_name = "SampleNeuralNet",
    output_dir = BUILD_PATH,
    backend = "Vitis",
    part = "xc7z010clg400-1",
    clock_period = 4, # t = 4ns <-> f = 250MHz
)

for layer in vitisModel.get_layers():
    print(layer.name, layer.__class__.__name__)

vitisModel.write()

## DSP REGISTER EDIT

# build_prj_file = pathlib.Path(BUILD_PATH + "/build_prj.tcl")

# build_prj_contents = build_prj_file.read_text()

# if ("config_schedule -enable_dsp_full_reg") not in build_prj_contents:
#     raise RuntimeError("Layout of build_prj.tcl unexpected!")

# edited_build_prj_contents = build_prj_contents.replace("config_schedule -enable_dsp_full_reg=false", "config_schedule -enable_dsp_full_reg=true")

# build_prj_file.write_text(edited_build_prj_contents)


