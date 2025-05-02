from datetime import datetime

from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from models.appointment import Appointment
from src.models.us_states import UsState
from src.models.insurance import InsurancePayer


class Patient(BaseModel):
    """
    A Patient represents an end user who can look to schedule appointments with clinicians
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    """Unique patient identifier"""

    first_name: str
    """Patient first name"""

    last_name: str
    """Patient last name"""

    state: UsState
    """US state where this patient resides"""

    insurance: InsurancePayer
    """The patient's insurance provider"""

    appointments: list[Appointment]
    """Appointments this patient currently has booked"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this patient was registered with our system"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this patient's information was most recently updated"""

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"Patient(id={self.id[:8]}...{self.id[-8:]}, first_name={self.first_name}, last_name={self.last_name}, state={self.state.value}, insurance={self.insurance.value})"

    @model_validator(mode="after")
    def appointments_for_self(self):
        if any(appointment.patient_id != self.id for appointment in self.appointments):
            raise ValueError(
                f"All appointments for {self} must be for patient_id {self.id}"
            )

        return self
