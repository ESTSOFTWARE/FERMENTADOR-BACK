from enum import Enum


class FermentationStatus(str, Enum):
    SCHEDULED   = "scheduled"
    RUNNING     = "running"
    COMPLETED   = "completed"
    INTERRUPTED = "interrupted"
