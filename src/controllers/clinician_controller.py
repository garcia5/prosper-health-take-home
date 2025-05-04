from collections import Counter
from dataclasses import dataclass
from datetime import timedelta

from db import Database
from models.clinician import AvailableSlot, Clinician
from models.patient import Patient
from models.requests import AppointmentCategory


@dataclass
class ClinicianController:
    """
    Perform tasks for clinicians
    """

    conn: Database

    def get_compatible_clinicians(
        self, patient: Patient, appointment_category: AppointmentCategory
    ) -> list[Clinician]:
        """
        Get all clinicians who can take an appointment with the given patient
        """
        clinicians = Clinician.load_all(self.conn)
        clinicians_for_appointment_type = [
            clinician
            for clinician in clinicians
            if clinician.is_patient_compatible(patient)
            and any(
                appt_type in clinician.allowed_appointment_types
                for appt_type in appointment_category.types
            )
        ]

        return clinicians_for_appointment_type

    def filter_availability_slots(
        self, clinician: Clinician, duration: int
    ) -> list[AvailableSlot]:
        """
        Filter the clinician's available_slots to maximize the number of [duration] minute
        appointments, taking into account their max availability + scheduled appointments
        """
        appointment_counter = Counter(
            [appointment.scheduled_for.date() for appointment in clinician.appointments]
        )

        duration_span = timedelta(minutes=duration)

        filtered_slots: list[AvailableSlot] = []

        availability_counter = Counter()
        for slot in sorted(clinician.available_slots, key=lambda slot: slot.date):
            # slot is too close to the previous one: filter it out
            if filtered_slots and slot.date < (filtered_slots[-1].date + duration_span):
                continue

            slot_date = slot.date.date()

            # check commitments for the current date - ignore any available slots if we're over
            # the clinician's limit
            committed_for_date = (
                availability_counter[slot_date] + appointment_counter[slot_date]
            )
            if committed_for_date >= clinician.max_daily_appointments:
                continue

            # check commitments over the past week
            # ASSUMPTION: "week" means a calendar week (Sunday - Saturday, inclusive), rather
            # than (Sunday - Sunday, inclusive)
            committed_for_week = 0
            for i in range(7):
                date = slot_date - timedelta(days=i)
                committed_for_week += (
                    availability_counter[date] + appointment_counter[date]
                )

            if committed_for_week >= clinician.max_weekly_appointments:
                continue

            availability_counter[slot_date] += 1
            filtered_slots.append(slot)

        return filtered_slots

    def get_follow_up_appointments(
        self,
        clinician: Clinician,
    ) -> dict[str, list[AvailableSlot]]:
        """
        Map each available slot to the list of follow up appointments that a patient can schedule
        after it

        A follow up appointment must be at least 1 day, but no more than 1 week, after the initial appointment
        """
        availability_follow_up_map: dict[str, list[AvailableSlot]] = {}

        for slot in clinician.available_slots:
            slot_date = slot.date.date()
            next_day = slot_date + timedelta(days=1)
            next_week = slot_date + timedelta(days=7)

            availability_follow_up_map[slot.id] = [
                availability
                for availability in clinician.available_slots
                if next_day <= availability.date.date() <= next_week
            ]

        return availability_follow_up_map
