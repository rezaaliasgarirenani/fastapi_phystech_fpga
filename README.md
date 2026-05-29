# Radiation-Resistant FPGA Selection API

This is a simple FastAPI REST service for a Python course project.

The topic is selection of radiation-resistant FPGA devices for space missions.
The project uses FastAPI, SQLite, SQLAlchemy, Pydantic schemas, JWT authentication,
CRUD endpoints, TestClient tests, and pylint.

## Main Idea

The API stores FPGA vendors, FPGA devices, users, and missions.

For a mission, the service can recommend suitable FPGA devices using simple
algorithmic logic. It checks radiation tolerance, logic cells, power limit, and
temperature range, then returns matching devices with a score.

## Database

The project uses SQLite.

The database file is created automatically when the app starts.

Main entities:

- users
- vendors
- fpga_devices
- missions

## API

The API includes:

- user registration and login
- JWT authorization
- CRUD endpoints
- FPGA recommendation endpoint
- Swagger UI for testing

Swagger is available after starting the app:

http://127.0.0.1:8000/docs

## Repository Structure

The repository root contains only the submission-facing files.

- `README.md` - project overview
- `INSTRUCTION.md` - run, demo, test, and pylint commands
- `LICENSE` - license file
- `requirements.txt` - Python dependencies
- `pylint.txt` - saved pylint output
- `service/` - FastAPI source code, tests, and pylint config
- `extra/` - submission links and extra course information

## How To Run And Test

For the actual commands and testing steps, check:

INSTRUCTION.md

## Pylint

The pylint result is saved in:

pylint.txt

## Author

Reza
