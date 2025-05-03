from dataclasses import dataclass
from typing import Self

from models import AvailableSlot, Clinician


@dataclass
class AvailabilityResponse:
    """
    An AvailabilityResponse represents a block of time available for a patient to book
    """

    clinician_first_name: str
    """First name for the clinician associated with this availability"""

    clinician_last_name: str
    """First name for the clinician associated with this availability"""

    clinician_id: str
    """Unique identifier for the clinician associated with this availability"""

    slot: AvailableSlot
    """The slot of time which is available"""

    follow_up_slot: AvailableSlot | None = None
    """If the appointment type requestsed requires a follow up, include that related available slot here"""
    """ASSUMPTION: follow up, if any, must be with the same psychatrist as the first appointment"""

    @classmethod
    def with_follow_up(cls, other: Self, follow_up_slot: AvailableSlot) -> Self:
        """
        Copy an existing available slot to add a follow up time
        """
        return cls(
            clinician_first_name=other.clinician_first_name,
            clinician_last_name=other.clinician_last_name,
            clinician_id=other.clinician_id,
            slot=other.slot,
            follow_up_slot=follow_up_slot,
        )

    @classmethod
    def from_clinician(cls, clinician: Clinician) -> list[Self]:
        return [
            cls(
                clinician_first_name=clinician.first_name,
                clinician_last_name=clinician.last_name,
                clinician_id=clinician.id,
                slot=slot,
            )
            for slot in clinician.available_slots
        ]

    @property
    def sort_fields(self):
        """
        Fields used for ordering
        """
        return (
            self.slot.date,
            self.clinician_last_name,
            self.clinician_first_name,
            self.clinician_id,
        )
