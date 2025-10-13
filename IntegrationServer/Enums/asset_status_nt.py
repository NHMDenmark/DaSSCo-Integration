from enum import Enum

class AssetStatusNT(Enum):
    WORKING_COPY = "WORKING_COPY"
    ISSUE_WITH_MEDIA = "ISSUE_WITH_MEDIA"
    ARCHIVE = "ARCHIVE"
    PROCESSING_HALTED = "PROCESSING_HALTED"
    BEING_PROCESSED = "BEING_PROCESSED"
    ISSUE_WITH_METADATA = "ISSUE_WITH_METADATA"
    PRE_PROCESSING = "PRE_PROCESSING"
    PROCESSING_ISSUE = "PROCESSING_ISSUE"
    AUDITING = "AUDITING"
    ERROR = "ERROR"
    DELETED = "DELETED"
    FOR_DELETION = "FOR_DELETION"
    CORRUPTED = "CORRUPTED"
    RESERVED = "RESERVED"
    PUBLISHED_TO_SPECIFY = "PUBLISHED_TO_SPECIFY"
    PUBLISHED_ALL = "PUBLISHED_ALL"

class AssetStatus:
    def __init__(self):
        self.WORKING_COPY = AssetStatusNT.WORKING_COPY.value
        self.ISSUE_WITH_MEDIA = AssetStatusNT.ISSUE_WITH_MEDIA.value
        self.ARCHIVE = AssetStatusNT.ARCHIVE.value
        self.PROCESSING_HALTED = AssetStatusNT.PROCESSING_HALTED.value
        self.BEING_PROCESSED = AssetStatusNT.BEING_PROCESSED.value
        self.ISSUE_WITH_METADATA = AssetStatusNT.ISSUE_WITH_METADATA.value
        self.PRE_PROCESSING = AssetStatusNT.PRE_PROCESSING.value
        self.PROCESSING_ISSUE = AssetStatusNT.PROCESSING_ISSUE.value
        self.AUDITING = AssetStatusNT.AUDITING.value
        self.ERROR = AssetStatusNT.ERROR.value
        self.DELETED = AssetStatusNT.DELETED.value
        self.FOR_DELETION = AssetStatusNT.FOR_DELETION.value
        self.CORRUPTED = AssetStatusNT.CORRUPTED.value
        self.RESERVED = AssetStatusNT.RESERVED.value
        self.PUBLISHED_TO_SPECIFY = AssetStatusNT.PUBLISHED_TO_SPECIFY.value
        self.PUBLISHED_ALL = AssetStatusNT.PUBLISHED_ALL.value