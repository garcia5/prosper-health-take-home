from enum import Enum

from models.appointment import AppointmentType


class AppointmentCategory(Enum):
    ASSESSMENT = "ASSESSMENT"
    THERAPY = "THERAPY"

    @property
    def types(self):
        match self.name:
            case "ASSESSMENT":
                return [
                    AppointmentType.ASSESSMENT_SESSION_1,
                    AppointmentType.ASSESSMENT_SESSION_2,
                ]
            case "THERAPY":
                return [
                    AppointmentType.THERAPY_INTAKE,
                    AppointmentType.THERAPY_SIXTY_MINS,
                ]
