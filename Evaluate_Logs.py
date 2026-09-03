import os
import json

### FUNCTIONS

def evaluateVitisLogs(logsDirPath):
    
    estimatedClockPeriodDict = {}
    
    for root, _, files in os.walk(logsDirPath):
        rootName = str(root)
        
        if ("vitis_run.log" in files):
            buildIdentifier = rootName.split("\\")[1] + "___" + rootName.split("\\")[2]
            estimatedClockPeriodsForFile = []
            with open(os.path.join(root, "vitis_run.log"), "r") as f:
                for line in f:
                    
                    if ("Estimated clock period" in line):
                        estimatedClockPeriod = line.split("Estimated clock period (")[1].split(")")[0]
                        if (estimatedClockPeriod not in estimatedClockPeriodsForFile):
                            estimatedClockPeriodsForFile.append(estimatedClockPeriod)
                            
                estimatedClockPeriodDict[buildIdentifier] = estimatedClockPeriodsForFile
                            
    return estimatedClockPeriodDict

def evaluateVivadoLogs(logsDirPath):
    
    dspFinalReportsOutput = ""
    
    for root, _, files in os.walk(logsDirPath):
        rootName = str(root)
        
        if ("Vivado_Analysis.log" in files or "Vivado_Analysis_Verilog.log" in files):
            buildIdentifier = rootName.split("\\")[1] + "___" + rootName.split("\\")[2]
            
            dspFinalReportsOutput += 60*"="
            dspFinalReportsOutput += "\n"
            dspFinalReportsOutput += buildIdentifier
            dspFinalReportsOutput += "\n"
            dspFinalReportsOutput += 60*"="
            dspFinalReportsOutput += "\n"
            dspFinalReportsOutput += "\n"

            if ("Vivado_Analysis_Verilog.log" in files):
                relevantLogFile = "Vivado_Analysis_Verilog.log"
            else:
                relevantLogFile = "Vivado_Analysis.log"
                
            with open(os.path.join(root, relevantLogFile), "r") as f:
                
                inDspFinalReportSection = False
                for line in f:
                    if ("DSP Final Report" in line):
                        inDspFinalReportSection = True
                        continue
                        
                    if (inDspFinalReportSection):
                        if (not line.startswith("+") and not line.startswith("|")):
                            inDspFinalReportSection = False
                            dspFinalReportsOutput += "\n"
                            break
                        
                        else:
                            dspFinalReportsOutput += line
                        
                                                    
    return dspFinalReportsOutput

def evaluateTimingSummaries(logsDirPath):
    
    timingSummariesOutput = ""
    
    for root, _, files in os.walk(logsDirPath):
        rootName = str(root)
        
        if ("Timing_Report_Implementation.rpt" in files):
            buildIdentifier = rootName.split("\\")[1] + "___" + rootName.split("\\")[2]
            
            timingSummariesOutput += 60*"="
            timingSummariesOutput += "\n"
            timingSummariesOutput += buildIdentifier
            timingSummariesOutput += "\n"
            timingSummariesOutput += 60*"="
            timingSummariesOutput += "\n"
            timingSummariesOutput += "\n"

                
            with open(os.path.join(root, "Timing_Report_Implementation.rpt"), "r") as f:
                
                lineCounter = 0
                for line in f:
                    if ("Design Timing Summary" in line):
                        lineCounter = 1
                        continue
                        
                    if (lineCounter >= 1 and lineCounter <= 3):
                        lineCounter = lineCounter + 1
                        continue
                    elif (lineCounter >= 4 and lineCounter <= 6):
                        lineCounter = lineCounter + 1
                        timingSummariesOutput += line
                        timingSummariesOutput += "\n"
                    elif (lineCounter >= 7):
                        break

                        
                                                    
    return timingSummariesOutput

def evaluateTimingPaths(logsDirPath):
    
    timingPathsEvaluationOutput = ""
    
    for root, _, files in os.walk(logsDirPath):
        rootName = str(root)
        
        if ("Timing_Paths_Implementation.rpt" in files):
            buildIdentifier = rootName.split("\\")[1] + "___" + rootName.split("\\")[2]
            
            dspArithmeticPaths = 0
            controlLogicPaths = 0
            
            timingPathsEvaluationOutput += 60*"="
            timingPathsEvaluationOutput += "\n"
            timingPathsEvaluationOutput += buildIdentifier
            timingPathsEvaluationOutput += "\n"
            timingPathsEvaluationOutput += 60*"="
            timingPathsEvaluationOutput += "\n"
            timingPathsEvaluationOutput += "\n"

            if ("Timing_Paths_Implementation.rpt" in files):
                
                with open(os.path.join(root, "Timing_Paths_Implementation.rpt"), "r") as f:
                    
                    for line in f:
                        if ("Slack (VIOLATED)" in line or "Source:" in line or "Destination:" in line):
   
                            timingPathsEvaluationOutput += line
                            timingPathsEvaluationOutput += "\n"
                            
                            if ("Destination:" in line):
                                if ("C[" in line or "A[" in line or "B[" in line or "P[" in line or "D[" in line) :
                                    dspArithmeticPaths = dspArithmeticPaths + 1
                                else:
                                    controlLogicPaths = controlLogicPaths + 1
                                
                                timingPathsEvaluationOutput += "\n"
                                timingPathsEvaluationOutput += 60*"-"
                                timingPathsEvaluationOutput += "\n"
                                timingPathsEvaluationOutput += "\n"
            
            timingPathsEvaluationOutput += "Top 20 kritische Pfade, die auf DSP-Arithmetik-Logik enden: " + str(dspArithmeticPaths) + "\n"
            timingPathsEvaluationOutput += "Top 20 kritische Pfade, die auf Kontroll-Logik enden: " + str(controlLogicPaths) + "\n"
            timingPathsEvaluationOutput += "\n"
                        
                                                    
    return timingPathsEvaluationOutput


# def 
                            
### MAIN SCRIPT

os.makedirs("./Evaluation", exist_ok = True)

estimatedClockPeriodDict = evaluateVitisLogs("./Remote_Files/Logs")
dspFinalReports = evaluateVivadoLogs("./Remote_Files/Logs")
timingSummaries = evaluateTimingSummaries("./Remote_Files/Logs")
timingPathsEvaluation = evaluateTimingPaths("./Remote_Files/Logs")

with open("./Evaluation/Vitis_Logs_Est_Clock_Periods.json", "w") as f:
    json.dump(estimatedClockPeriodDict, f, indent = 2)
    
with open("./Evaluation/DSP_Final_Reports.txt", "w") as f:
    f.write(dspFinalReports)
                            
with open("./Evaluation/Timing_Summaries.txt", "w") as f:
    f.write(timingSummaries)        
                            
with open("./Evaluation/Timing_Paths_Evaluation.txt", "w") as f:
    f.write(timingPathsEvaluation)
                                
                    