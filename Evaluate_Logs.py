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





# def 
                            
### MAIN SCRIPT

os.makedirs("./Evaluation", exist_ok = True)

estimatedClockPeriodDict = evaluateVitisLogs("./Remote_Files/Logs")

with open("./Evaluation/Vitis_Logs_Est_Clock_Periods.json", "w") as f:
    json.dump(estimatedClockPeriodDict, f, indent = 2)
                                    
                            
                            
                                
                    