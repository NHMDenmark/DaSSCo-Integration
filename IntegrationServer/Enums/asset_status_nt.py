from enum import Enum

class AssetStatusNT(Enum):
    WORKING_COPY = "WORKING_COPY"
    ISSUE_WITH_MEDIA = "ISSUE_WITH_MEDIA"
    ARCHIVE = "ARCHIVE"
    FOR_DELETION = "FOR_DELETION"
    PROCESSING_HALTED = "PROCESSING_HALTED"
    BEING_PROCESSED = "BEING_PROCESSED"
    ISSUE_WITH_METADATA = "ISSUE_WITH_METADATA"

class AssetStatus:
    def __init__(self):
        self.WORKING_COPY = AssetStatusNT.WORKING_COPY.value
        self.ISSUE_WITH_MEDIA = AssetStatusNT.ISSUE_WITH_MEDIA.value
        self.ARCHIVE = AssetStatusNT.ARCHIVE.value
        self.FOR_DELETION = AssetStatusNT.FOR_DELETION.value
        self.PROCESSING_HALTED = AssetStatusNT.PROCESSING_HALTED.value
        self.BEING_PROCESSED = AssetStatusNT.BEING_PROCESSED.value
        self.ISSUE_WITH_METADATA = AssetStatusNT.ISSUE_WITH_METADATA.value