from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from db import Database
from models.appointment import Appointment, AppointmentType
from models.insurance import InsurancePayer
from models.patient import Patient
from models.us_states import UsState


class AvailableSlot(BaseModel):
    """
    An AvailableSlot represents an open block of time that a patient can schedule
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

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

    @classmethod
    def load_all(cls, conn: Database, clinician_id: str):
        """
        Fetch all available slots for the given clinitian from the "database"
        """

        # ASSUMPTION:
        # The "database" is purged of availability that is in the past
        return [cls.model_validate(slot) for slot in conn.available_slots.get()]


class ClinicianType(Enum):
    THERAPIST = "THERAPIST"
    PSYCHOLOGIST = "PSYCHOLOGIST"


class Clinician(BaseModel):
    """
    A Clinician represents a professional who can schedule appointments with patients
    """

    # Make sure we're validating data as we try to updte the clinician's data
    model_config = ConfigDict(
        validate_assignment=True, alias_generator=to_camel, populate_by_name=True
    )

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

    appointments: list[Appointment] = []
    """Appointments this clinician currently has booked"""

    available_slots: list[AvailableSlot] = []
    """Open appointment slots this clinician currently has available"""

    max_daily_appointments: int
    """Maximum number of appointments per day this clinician can accept"""

    max_weekly_appointments: int
    """Maximum number of appointments per week this clinician can accept"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this clinician was registered with our system"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this clinician's information was most recently updated"""

    @property
    def allowed_appointment_types(self):
        """Types of appointments this clinician is allowed to schedule"""
        if self.clinician_type == ClinicianType.PSYCHOLOGIST:
            return [
                AppointmentType.ASSESSMENT_SESSION_1,
                AppointmentType.ASSESSMENT_SESSION_2,
            ]

        return [
            AppointmentType.THERAPY_INTAKE,
            AppointmentType.THERAPY_SIXTY_MINS,
        ]

    def is_patient_compatible(self, patient: Patient) -> bool:
        """
        Return whether or not the patient's insrance/state is accepted by this clinician
        """
        return patient.state in self.states and patient.insurance in self.insurances

    @classmethod
    def load_all(cls, conn: Database):
        """
        Fetch all clinicians from the "database"
        """
        return [
            cls.model_validate(
                {
                    **clinician,
                    "available_slots": AvailableSlot.load_all(conn, clinician["id"]),
                    "appointments": Appointment.load(
                        conn, clinician_id=clinician["id"]
                    ),
                }
            )
            for clinician in conn.clinicians.get()
        ]

    @classmethod
    def load(cls, conn: Database, clinician_id: str):
        return cls.model_validate(
            {
                **conn.clinicians.get(clinician_id),
                "available_slots": AvailableSlot.load_all(conn, clinician_id),
                "appointments": Appointment.load(conn, clinician_id=clinician_id),
            }
        )

    def __str__(self):
        return (
            f"[{self.clinician_type.value.upper()}] {self.first_name} {self.last_name}"
        )
