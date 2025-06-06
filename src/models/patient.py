from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from db import Database
from models.appointment import Appointment
from models.insurance import InsurancePayer
from models.us_states import UsState


class Patient(BaseModel):
    """
    A Patient represents an end user who can look to schedule appointments with clinicians
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

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

    appointments: list[Appointment] = []
    """Appointments this patient currently has booked"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this patient was registered with our system"""

    created_at: datetime = Field(default_factory=datetime.now)
    """Timestamp when this patient's information was most recently updated"""

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def load_all(cls, conn: Database):
        """
        Fetch patients from the "database"
        """
        return [
            cls.model_validate(
                {
                    **patient,
                    "appointments": Appointment.load(conn, patient_id=patient["id"]),
                }
            )
            for patient in conn.patients.get()
        ]

    @classmethod
    def load(cls, conn: Database, patient_id: str):
        return cls.model_validate(
            {
                **conn.patients.get(patient_id),
                "appointments": Appointment.load(conn, patient_id=patient_id),
            }
        )
