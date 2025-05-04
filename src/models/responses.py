from dataclasses import dataclass
from itertools import chain
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
    """
    If the appointment type requestsed requires a follow up, include that related available slot here
    ASSUMPTION: follow up, if any, must be with the same psychatrist as the first appointment
    """

    @classmethod
    def from_clinician(
        cls,
        clinician: Clinician,
        follow_up_slots: dict[str, list[AvailableSlot]] | None = None,
    ) -> list[Self]:
        """
        Transform a clinician and their availability into a response model

        If follow_up_slots is provided, it must be a mapping of
        AvailableSlot id -> all AvailableSlots which can be scheduled for follow up
        """
        if not follow_up_slots:
            return [
                cls(
                    clinician_first_name=clinician.first_name,
                    clinician_last_name=clinician.last_name,
                    clinician_id=clinician.id,
                    slot=slot,
                )
                for slot in clinician.available_slots
            ]

        return list(
            chain(
                *[
                    [
                        cls(
                            clinician_first_name=clinician.first_name,
                            clinician_last_name=clinician.last_name,
                            clinician_id=clinician.id,
                            slot=slot,
                            follow_up_slot=follow_up_slot,
                        )
                        for follow_up_slot in follow_up_slots.get(slot.id, [])
                    ]
                    for slot in clinician.available_slots
                ]
            )
        )

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
