import keras
import hls4ml

import numpy as np
import os
import json
import pathlib

### Keras definition and initalization of neural network

os.makedirs("./SampleNeuralNets", exist_ok = True)


weights1 = np.array([
    [2,     -4,     0,      -7,         5,      3,      9,      -3],
    [2,     4,      5,      0,          3,      -7,     3,      7],
    [2,     3,      -7,     -11,        0,      -7,     3,      9],
    [2,     4,      3,      -11,        3,      0,      3,      9],
    [2,     7,      5,      11,         3,      9,      0,      5],
    [2,     -9,     3,      3,          3,      -9,     3,      0],
    [0,     4,      5,      -3,         3,      -9,     -7,     7],
    [2,     0,      3,      -11,        3,      9,      3,      9]
])

weights2 = np.array([
    [2,     4,      5,      0,          3,      -7,     3,      7],
    [2,     3,      -7,     -11,        0,      -7,     3,      9],
    [2,     -4,     0,      -7,         5,      3,      9,      -3],
    [2,     4,      3,      -11,        3,      0,      3,      9],
    [2,     -9,     3,      3,          3,      -9,     3,      0],
    [0,     4,      5,      -3,         3,      -9,     -7,     7],
    [2,     0,      3,      -11,        3,      9,      3,      9],
    [2,     7,      5,      11,         3,      9,      0,      5]
])

weights3 = np.array([
    [2,     3,      -7,     -11,        0,      -7,     3,      9],
    [2,     -9,     3,      3,          3,      -9,     3,      0],
    [0,     4,      5,      -3,         3,      -9,     -7,     7],
    [2,     4,      3,      -11,        3,      0,      3,      9],
    [2,     7,      5,      11,         3,      9,      0,      5],
    [2,     0,      3,      -11,        3,      9,      3,      9],
    [2,     -4,     0,      -7,         5,      3,      9,      -3],
    [2,     4,      5,      0,          3,      -7,     3,      7]
])

bias1 = np.array([2, -4, 3, 5, 7, 11, -7, 3])

bias2 = np.array([11, -7, 3, 2, -4, 3, 5, 7])

bias3 = np.array([20, -4, 3, -7, 3, 5, 7, 11])

model = keras.Sequential([
    keras.Input(shape = (8,)),
    
    keras.layers.Dense(8, activation = None, name = "dense1"),
    keras.layers.ReLU(name = "relu1"),
    keras.layers.Dense(8, activation = None, name = "dense2"),
    keras.layers.ReLU(name = "relu2"),
    keras.layers.Dense(8, activation = None, name = "dense3"),
    keras.layers.ReLU(name = "relu3")
])

model.get_layer("dense1").set_weights([weights1, bias1])
model.get_layer("dense2").set_weights([weights2, bias2])
model.get_layer("dense3").set_weights([weights3, bias3])

model.summary()
    
### hls4ml conversion
config = hls4ml.utils.config_from_keras_model(
    model,
    granularity = "name",
    backend = "Vitis",
    default_precision = "int<16>",
    default_reuse_factor = 8,
)

for denseName in ["dense1", "dense2", "dense3"]:

    config["LayerName"][denseName]["Precision"]["weight"] = "int<16>"
    config["LayerName"][denseName]["Precision"]["bias"] = "int<16>"
    config["LayerName"][denseName]["Precision"]["accum"] = "int<48>"
    config["LayerName"][denseName]["Precision"]["result"] = "int<48>"
    
    config["LayerName"][denseName]["ReuseFactor"] = 8
    config["LayerName"][denseName]["Strategy"] = "Resource"
    
for reluName in ["relu1", "relu2", "relu3"]:
    config["LayerName"][reluName]["Precision"]["result"] = "int<16>"
    config["LayerName"][reluName]["Strategy"] = "Resource"
    
config["LayerName"]["input_layer"]["Precision"]["result"] = "int<16>"

with open("Vitis_HLS_Config.json", "w") as f:
    json.dump(config, f, indent = 2)
    
BUILD_NAME = "Reuse8_Edited"
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

vitisModel.write()

## DSP REGISTER EDIT


build_prj_file = pathlib.Path(BUILD_PATH + "/build_prj.tcl")

build_prj_contents = build_prj_file.read_text()

if ("config_schedule -enable_dsp_full_reg") not in build_prj_contents:
    raise RuntimeError("Layout of build_prj.tcl unexpected!")

edited_build_prj_contents = build_prj_contents.replace("config_schedule -enable_dsp_full_reg=false", "config_schedule -enable_dsp_full_reg=true")

build_prj_file.write_text(edited_build_prj_contents)


