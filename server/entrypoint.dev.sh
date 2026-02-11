#!/bin/bash

python manage.py makemigrations
python manage.py migrate
pytest -s 