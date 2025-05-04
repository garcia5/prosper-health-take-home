# Prosper Health Take Home
## Getting Started

### Prerequisites

- Python 3.11 or newer
- [uv](https://github.com/astral-sh/uv) installed on your system

### Setup

1. Install dependencies
```bash
uv sync --all-groups
```

2. (optional) Install pre-commit hooks
```bash
uv run pre-commit install
```

## Usage
```bash
uv run python ./src/main.py get-open-slots
```

## Project Structure
```
src/
├── controllers/
├── db/
│   └── data/
├── main.py
└── models/
```

### Db

The `db` module defines the mock database connection, allowing the models to fetch data from json files stored under
`db/data/`. It exports a `Database` class, which must be used to actually fetch data

### Models

The `models` module defines "ORM" classes that map to database objects, as well as "user facing" data models. Most
models have convenience methods attached to facilitate common operations

Models are defined using [pydantic](https://docs.pydantic.dev/latest/)

In practice, these would be defined using a real ORM such as [sqlalchemy](https://www.sqlalchemy.org/), and support querying/filtering

### Controllers

The `controllers` module defines the bulk of the business logic associated with `models`. For this project, the
requirements were only to return clinician availability for a given patient, so only the clinician controller is
implemented.

In practice, the clinicain controller would likely have more methods to manage Clinician information/availability. There
would be an "appointments controller" for managing appointments for both patients and clinicians, and a "patient
controller" for managing patient information.

### main.py

`main.py` defines the entrypoint into the application. It is responsible for instantiating the "database" connection and
application controller(s). It is wrapped by a [click](https://click.palletsprojects.com/en/stable/) CLI program, which
handles user I/O.

In practice, this would likely be a [Flask](https://flask.palletsprojects.com/en/stable/) app, rather than `click`.

## Project Notes

Any assumptions are documented throughout the code in comments, indicated by "ASSUMPTION". In summary:

- Assume all clinician availability is *always* in the future for the date a patient is requesting it
- Assume `ASSESSMENT_1` and `ASSESSMENT_2` appointments *must* be booked for the same clinician
- Assume a patient *must* provide the type of appointment they want to schedule when looking for availability

## References

- [Instructions](https://prosper-health.notion.site/Prosper-Health-Engineering-Take-Home-115483f1ec5780deaf59efbcd2bdd4c4#f84361ddca844ef783d321c0f38e6979)
- [Click](https://click.palletsprojects.com/en/stable/)
- [Pydantic](https://docs.pydantic.dev/latest/)
