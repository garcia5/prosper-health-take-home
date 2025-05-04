from itertools import chain

import click

from controllers.clinician_controller import ClinicianController
from db import Database
from models import AppointmentCategory, AvailabilityResponse, Patient

DEFAULT_PATIENT_ID = (
    "70801084-e022-4a09-a6ca-62103b3565eb"  # see ./db/data/patients.json for source
)
DEFAULT_APPOINTMENT_TYPE = "ASSESSMENT"  # see ./models/requests.py for options


class App:
    def __init__(self):
        self.db = Database.init()
        self.clinician_controller = ClinicianController(self.db)

    def get_available_slots(
        self,
        patient_id: str,
        appointment_category: AppointmentCategory,
    ):
        """
        Get all open appointment slots that a Patient can book for a given "type" of appointment

        ASSUMPTION: patient must provide the type of appointment they are looking for when
                    searching for clinician availability
        """

        # First, load only clinicians that accept the patient's insurance/state,
        # and who are the correct "type" to handle this category of appointment
        patient = Patient.load(self.db, patient_id)
        compatible_clinians = self.clinician_controller.get_compatible_clinicians(
            patient, appointment_category
        )

        # Limit each clinician's availability so that
        # 1. only non-overlapping slots are shown
        # 2. availability is only shown if the clinician is not already "full" for that day/week
        duration = 90 if appointment_category == AppointmentCategory.ASSESSMENT else 60
        for clinician in compatible_clinians:
            clinician.available_slots = (
                self.clinician_controller.filter_availability_slots(clinician, duration)
            )

        # For patients looking to book an initial assessment, they must also book the follow up
        # assessment at the same time
        # For each clinician, map from their initial availability to all eligible follow up slots
        # example:
        # {
        #   "clinician-1-id": {"2025-05-04 @ 12:00": ["2025-05-05 @ 12:00", "2025-05-05 @ 13:30"]}
        #   "clinician-2-id": {"2025-05-04 @ 12:00": ["2025-05-05 @ 12:00", "2025-05-05 @ 13:30"]}
        # }
        clinician_follow_up_appointments = {}
        if appointment_category == AppointmentCategory.ASSESSMENT:
            for clinician in compatible_clinians:
                clinician_follow_up_appointments[clinician.id] = (
                    self.clinician_controller.get_follow_up_appointments(clinician)
                )

        # Map clinicians with their availability to a user-friendly response model, excluding private clinician information like
        # maxDailyAppointments/maxWeeklyAppointments
        clinician_availability = {
            clinician.id: AvailabilityResponse.from_clinician(
                clinician,
                follow_up_slots=clinician_follow_up_appointments.get(clinician.id),
            )
            for clinician in compatible_clinians
        }

        flattened_availability = list(chain(*clinician_availability.values()))

        # Return all clinician availability in chronological order, grouped by clinician
        return list(
            sorted(
                flattened_availability,
                key=lambda rsp: rsp.sort_fields,
            )
        )


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    ctx.obj = App()


@cli.command()
@click.pass_obj
# options commented out for easier testing
# @click.option(
#     "--patient-id",
#     prompt=True,
#     default=DEFAULT_PATIENT_ID,
# )
# @click.option(
#     "--appointment-type",
#     type=click.Choice([category.name for category in AppointmentCategory]),
#     prompt=True,
#     show_choices=True,
#     default=DEFAULT_APPOINTMENT_TYPE,
# )
def get_open_slots(
    app: App,
    patient_id: str = DEFAULT_PATIENT_ID,
    appointment_type: str = DEFAULT_APPOINTMENT_TYPE,
):
    slots = app.get_available_slots(patient_id, AppointmentCategory[appointment_type])
    click.echo("Availability")
    click.echo("------------")
    for slot in slots:
        date_fmt = "%a, %b %d @ %I:%M %p"
        if slot.follow_up_slot:
            click.echo(
                f"({slot.slot.date.strftime(date_fmt)}, {slot.follow_up_slot.date.strftime(date_fmt)}) with {slot.clinician_first_name} {slot.clinician_last_name}"
            )
        else:
            click.echo(
                f"{slot.slot.date.strftime(date_fmt)} with {slot.clinician_first_name} {slot.clinician_last_name}"
            )


if __name__ == "__main__":
    cli()
