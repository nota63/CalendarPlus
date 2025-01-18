#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files for Django
python manage.py collectstatic --noinput

# You can add other build steps here if necessary, like migrations
# python manage.py migrate
