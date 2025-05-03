from dataclasses import dataclass
from datetime import datetime, timedelta

from db import Database
from models import (
    AppointmentCategory,
    AvailabilityResponse,
    Clinician,
    Patient,
)


@dataclass
class PatientController:
    """
    Perform tasks for patients
    """

    conn: Database

    def get_available_slots(
        self,
        patient_id: str,
        appointment_category: AppointmentCategory,
    ) -> list[AvailabilityResponse]:
        """
        Get a list of all appointment time slots that are available for the patient to book
        """
        patient = Patient.load(self.conn, patient_id)
        clinicians = Clinician.load_all(self.conn)

        compatible_clinicians = filter(
            lambda clinician: clinician.is_patient_compatible(patient),
            clinicians,
        )

        if appointment_category is not None:
            # Filter to only clinicians who can provide this type of appointment
            compatible_clinicians = filter(
                lambda clinician: any(
                    appointment_type in clinician.allowed_appointment_types
                    for appointment_type in appointment_category.types
                ),
                compatible_clinicians,
            )

        available_slots: list[AvailabilityResponse] = []
        for clinician in compatible_clinicians:
            available_slots += AvailabilityResponse.from_clinician(clinician)

        if appointment_category != AppointmentCategory.ASSESSMENT:
            return list(
                sorted(
                    available_slots, key=lambda availability: availability.sort_fields
                )
            )

        # For assessments, we want to schedule both appointments 1 and 2 at the same time
        # No more than 7 days apart, but not on the same day
        # Populate the follow_up_slot property of all openings accordingly
        availability_with_pairs: list[AvailabilityResponse] = []
        for availability in available_slots:
            availability_date = availability.slot.date
            next_day = availability_date + timedelta(days=1)
            seven_days_out = availability_date + timedelta(days=7)

            available_pairs = [
                follow_up
                for follow_up in available_slots
                if next_day <= follow_up.slot.date <= seven_days_out
                and follow_up.clinician_id == availability.clinician_id
            ]

            availability_with_pairs += [
                AvailabilityResponse.with_follow_up(availability, pair.slot)
                for pair in available_pairs
            ]

        return list(
            sorted(
                availability_with_pairs,
                key=lambda availability: availability.sort_fields,
            )
        )

    def optimize_appointment_slots(
        self,
        all_availability: list[AvailabilityResponse],
        duration: int,
    ) -> list[AvailabilityResponse]:
        """
        For the given *sorted* list of availability, filter is so no 2 appointments are less than [duration]
        minutes apart, maximizing the number of availability slots remaining

        - all_availability *must* be sorted!
        """

        if not all_availability:
            return []

        # keep track of the last availability we've seen for each clinician
        # map of clinician_id -> last availability slot seen
        last: dict[str, datetime] = {}
        filtered = []
        for availability in all_availability:
            clinician_id = availability.clinician_id
            availability_start = availability.slot.date

            if (most_recent_for_clinician := last.get(clinician_id)) is None:
                last[clinician_id] = availability_start

            elif availability_start >= (
                most_recent_for_clinician + timedelta(minutes=duration)
            ):
                last[clinician_id] = availability_start
                filtered.append(availability)

        return filtered
