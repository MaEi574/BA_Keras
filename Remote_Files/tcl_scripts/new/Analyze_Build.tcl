read_vhdl [glob ./SampleNeuralNet_prj/solution1/syn/vhdl/*.vhd]

read_xdc ./Analysis_Constraints.xdc

file mkdir ./Analysis

# ============================================================
# Synthesis
# ============================================================

synth_design \
    -top SampleNeuralNet \
    -part xc7z010clg400-1 \
    -mode out_of_context

# ============================================================
# Post-Synthesis Analysis
# ============================================================

report_timing_summary -file ./Analysis/Timing_Report_Synthesis.rpt
report_timing -max_paths 20 -file ./Analysis/Timing_Paths_Synthesis.rpt

report_utilization -hierarchical -file ./Analysis/Utilization_Report_Synthesis.rpt

# ============================================================
# DSP48E1 Inspection
# ============================================================

set dsps [get_cells -hierarchical -filter {REF_NAME == DSP48E1}]

set fh [open "./Analysis/DSP_Properties.rpt" w]

puts $fh "DSP48E1 count: [llength $dsps]"
puts $fh ""

foreach dsp $dsps {
    puts $fh "--------------------------------------------------"
    puts $fh "DSP: $dsp"

    foreach prop {
        AREG
        BREG
        MREG
        PREG
        CREG
        OPMODEREG
        ALUMODEREG
        USE_MULT
        PRIMITIVE_TYPE
    } {
        puts $fh "$prop = [get_property $prop $dsp]"
    }

    puts $fh ""
}

close $fh

write_checkpoint -force ./Analysis/Post_Synthesis.dcp

# ============================================================
# Implementation
# ============================================================

opt_design
place_design
route_design

# ============================================================
# Post-Implementation Analysis
# ============================================================

report_timing_summary -file ./Analysis/Timing_Report_Implementation.rpt
report_timing -max_paths 20 -file ./Analysis/Timing_Paths_Implementation.rpt
report_utilization -hierarchical -file ./Analysis/Utilization_Report_Implementation.rpt

write_checkpoint -force ./Analysis/Post_Implementation.dcp