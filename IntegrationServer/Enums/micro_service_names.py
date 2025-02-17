from enum import Enum

"""
Enums for service names. Note the prefix/abbreviation are not exactly as the actual prefixes. 
"""
class MicroServiceNamesEnum(Enum):
        ESA = "Erda sync ARS"
        CFSA = "Close file share ARS"
        OFSA = "Open file share ARS"
        ACA = "Asset creator ARS"
        VESA = "Validate erda sync ARS"
        FUA = "File uploader ARS"
        UMA = "Update metadata ARS"
        ACH = "Asset creator HPC"
        HCUS = "HPC clean up service"
        HJC = "HPC job caller"
        HJRH = "HPC job retry handler"
        HUJH = "HPC unresponsive job handler"
        HFU = "HPC file uploader"
        NFFN = "New files finder (Ndrive)"
        PNFN = "Process new files (Ndrive)"
        DFN = "Delete files (Ndrive)"
        DLF = "Delete local files"
        APSH = "Asset paused status handler"
        FPSH = "Flag paused status handler"
        AESH = "Asset error status handler"
        THS = "Throttle service"

class MicroServiceNames:
    def __init__(self):
        pass