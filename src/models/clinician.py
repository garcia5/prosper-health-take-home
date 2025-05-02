from datetime import datetime
from enum import Enum
from itertools import groupby
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from models.appointment import Appointment, AppointmentType
from models.insurance import InsurancePayer
from models.us_states import UsState


class AvailableSlot(BaseModel):
    """
    An AvailableSlot represents an open block of time that a patient can schedule
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    """Unique slot identifier"""

    date: datetime
    """Start date and time of the available slot"""

    length: int
    """Open slot length, in minutes"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this available slot was first created"""

    updated_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this available slot was most recently updated"""


class ClinicianType(Enum):
    THERAPIST = "Therapist"
    PSYCHOLOGIST = "Psychologist"


class Clinician(BaseModel):
    """
    A Clinician represents a professional who can schedule appointments with patients
    """

    # Make sure we're validating data as we try to updte the clinician's data
    model_config = ConfigDict(validate_assignment=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    """Clinician unique identifier"""

    first_name: str
    """Clinician first name"""

    last_name: str
    """Clinician last name"""

    states: list[UsState]
    """US states where this clinician is allowed to practice"""

    insurances: list[InsurancePayer]
    """Insurance providers this clinician accepts"""

    clinician_type: ClinicianType
    """Type of clinician"""

    appointments: list[Appointment]
    """Appointments this clinician currently has booked"""

    available_slots: list[AvailableSlot]
    """Open appointment slots this clinician currently has available"""

    max_daily_appointments: int
    """Maximum number of appointments per day this clinician can accept"""

    max_weekly_appointments: int
    """Maximum number of appointments per week this clinician can accept"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this clinician was registered with our system"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this clinician's information was most recently updated"""

    def __str__(self):
        return (
            f"[{self.clinician_type.value.upper()}] {self.first_name} {self.last_name}"
        )

    def __repr__(self):
        return f"Clinician(type={self.clinician_type}, id={self.id[:8]}...{self.id[-8:]}, first_name={self.first_name}, last_name={self.last_name})"

    @model_validator(mode="after")
    def appointments_must_be_for_clinician(self):
        if any(
            appointment.clinician_id != self.id for appointment in self.appointments
        ):
            raise ValueError(
                f"All appointments for {self} must be for clinician_id {self.id}"
            )

        return self

    @model_validator(mode="after")
    def respect_max_appointments(self):
        for day, daily_appointments in groupby(
            self.appointments, key=lambda appt: appt.scheduled_for.date
        ):
            num_daily_appointments = len(list(daily_appointments))
            if num_daily_appointments > self.max_daily_appointments:
                raise ValueError(
                    f"Clinician {self} can only accept up to {self.max_daily_appointments} per day (found {num_daily_appointments} for {day})"
                )

        for (week_num, year), weekly_appointments in groupby(
            self.appointments,
            key=lambda appt: (
                appt.scheduled_for.isocalendar()[1],
                appt.scheduled_for.year,
            ),
        ):
            num_weekly_appointments = len(list(weekly_appointments))
            if num_weekly_appointments > self.max_weekly_appointments:
                raise ValueError(
                    f"Clinician {self} can only accept up to {self.max_weekly_appointments} per week (found {num_weekly_appointments} for week {week_num}, {year})"
                )

        return self

    @model_validator(mode="after")
    def correct_appointment_type(self):
        if self.clinician_type == ClinicianType.PSYCHOLOGIST:
            expected_appointment_types = [
                AppointmentType.ASSESSMENT_SESSION_1,
                AppointmentType.ASSESSMENT_SESSION_2,
            ]
        else:
            expected_appointment_types = [
                AppointmentType.THERAPY_INTAKE,
                AppointmentType.THERAPY_SIXTY_MINS,
            ]

        if any(
            appointment.appointment_type not in expected_appointment_types
            for appointment in self.appointments
        ):
            raise ValueError(
                f"Clinician {self} can only acccept {expected_appointment_types} appointments"
            )

        return self
