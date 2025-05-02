from enum import Enum


class InsurancePayer(Enum):
    """
    Accepted insruance providers
    """

    AETNA = "AETNA"
    BCBS = "BCBS"
    CIGNA = "CIGNA"
    UNITED = "UNITED"
