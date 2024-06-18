from enum import Enum

class FileFormatNT(Enum):
    TIF = "TIF"
    JPEG = "JPEG"
    RAW = "RAW"
    RAF = "RAF"
    CR3 = "CR3"
    DNG = "DNG"
    TXT = "TXT"

class FileFormat:
    def __init__(self):
        self.TIF = FileFormat.TIF.value
        self.JPEG = FileFormat.JPEG.value
        self.RAW = FileFormat.RAW.value
        self.RAF = FileFormat.RAF.value
        self.CR3 = FileFormat.CR3.value
        self.DNG = FileFormat.DNG.value
        self.TXT = FileFormat.TXT.value