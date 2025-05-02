from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class AppointmentType(Enum):
    ASSESSMENT_SESSION_1 = "ASSESSMENT_SESSION_1"
    ASSESSMENT_SESSION_2 = "ASSESSMENT_SESSION_2"
    THERAPY_INTAKE = "THERAPY_INTAKE"
    THERAPY_SIXTY_MINS = "THERAPY_SIXTY_MINS"


class AppointmentStatus(Enum):
    UPCOMING = "UPCOMING"
    OCCURRED = "OCCURRED"
    NO_SHOW = "NO_SHOW"
    RE_SCHEDULED = "RE_SCHEDULED"
    CANCELLED = "CANCELLED"
    LATE_CANCELLATION = "LATE_CANCELLATION"


class Appointment(BaseModel):
    """
    An Appointment represents a booked meeting between a patient and a clinician
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    """Unique appointment identifier"""

    patient_id: str
    """Patient associated with the appointment"""

    clinician_id: str
    """Clinician responsible for the appointment"""

    scheduled_for: datetime
    """Timestamp when this appointment starts"""

    appointment_type: AppointmentType
    """Type of appointment"""

    status: AppointmentStatus
    """Status of the appointment"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when the appointment was created"""

    updated_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this appointment was most recently updated"""
