# Instructions

All shell commands below are run from the repository root unless another path is shown.

1) Install packages

python -m pip install -r requirements.txt

2) Start the server

cd service

python -m uvicorn app.main:app --reload

3) Open this page

http://127.0.0.1:8000/docs

4) Open health section

Click GET /

Click Try it out

Click Execute

5) Open vendors section

Click GET /vendors/

Click Try it out

Click Execute

6) Open fpga_devices section

Click GET /fpga-devices/

Click Try it out

Click Execute

7) Open recommendations section

Click POST /recommendations/

Click Try it out

Use this request body:

{
  "required_tid_krad": 50,
  "min_logic_cells": 100000,
  "max_power_w": 8,
  "required_temp_min_c": -40,
  "required_temp_max_c": 85
}

Click Execute

8) Open auth section

Click POST /auth/login

Click Try it out

Use:

username: demo@example.com

password: demo123

Click Execute

9) Click Authorize at the top of Swagger

Use:

username: demo@example.com

password: demo123

Click Authorize

Click Close

10) Open auth section again

Click GET /auth/me

Click Try it out

Click Execute

11) Open missions section

Click GET /missions/

Click Try it out

Click Execute

12) Open recommendations section again

Click GET /recommendations/mission/{mission_id}

Click Try it out

Use:

mission_id: 1

Click Execute

13) Show the business logic file

service/app/recommendation.py

14) Run tests

Open a new terminal from the repository root, then run:

cd service

python -m pytest

15) Run pylint

Open a terminal from the repository root, then run:

cd service

python -m pylint app > ../pylint.txt

Get-Content ../pylint.txt

16) If port 8000 is busy

python -m uvicorn app.main:app --reload --port 8010

Open:

http://127.0.0.1:8010/docs
