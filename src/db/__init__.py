from dataclasses import dataclass
import json
from typing import overload


@dataclass
class Table:
    """
    'Table' implementation backed by json lists of dicts
    """

    source: str

    @overload
    def get(self, id: str) -> dict: ...

    @overload
    def get(self) -> list[dict]: ...

    @overload
    def get(self, id: None) -> list[dict]: ...

    def get(self, id: str | None = None) -> list[dict] | dict:
        """
        Load item(s) from this table

        If `id` is given, return the row with the corresponding `id` from the table.
        Otherwise, return the entire collection
        """
        with open(self.source, "r") as data:
            raw_data = json.load(data)

        if id is None:
            return raw_data

        return next(
            (row for row in raw_data if "id" in row and row["id"] == id), raw_data[0]
        )


@dataclass
class Database:
    """
    Mock database implementation
    """

    patients: Table
    clinicians: Table
    appointments: Table
    available_slots: Table

    @classmethod
    def init(cls):
        return cls(
            patients=Table(source="./src/db/data/patients.json"),
            clinicians=Table(source="./src/db/data/clinicians.json"),
            appointments=Table(source="./src/db/data/appointments.json"),
            available_slots=Table(source="./src/db/data/slots.json"),
        )
