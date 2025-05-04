from itertools import chain

import click

from controllers.clinician_controller import ClinicianController
from db import Database
from models import AppointmentCategory, AvailabilityResponse, Patient

DEFAULT_PATIENT_ID = "70801084-e022-4a09-a6ca-62103b3565eb"
DEFAULT_APPOINTMENT_TYPE = "ASSESSMENT"


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
        """
        patient = Patient.load(self.db, patient_id)
        compatible_clinians = self.clinician_controller.get_compatible_clinicians(
            patient, appointment_category
        )

        duration = 90 if appointment_category == AppointmentCategory.ASSESSMENT else 60
        for clinician in compatible_clinians:
            clinician.available_slots = (
                self.clinician_controller.filter_availability_slots(clinician, duration)
            )

        clinician_follow_up_appointments = {}
        if appointment_category == AppointmentCategory.ASSESSMENT:
            for clinician in compatible_clinians:
                clinician_follow_up_appointments[clinician.id] = (
                    self.clinician_controller.get_follow_up_appointments(clinician)
                )

        clinician_availability = {
            clinician.id: AvailabilityResponse.from_clinician(
                clinician,
                follow_up_slots=clinician_follow_up_appointments.get(clinician.id),
            )
            for clinician in compatible_clinians
        }

        flattened_availability = list(chain(*clinician_availability.values()))

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
