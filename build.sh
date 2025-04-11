#!/usr/bin/env bash

# Exist on error
set -o errexit

# Modify this line as needed for package manager
pip install -r requiremenets.txt

# Convert static files
python manage.py collectstatic --no-input


# Apply any outstanding database migrations
python manage.py migrate

# Update pip
#python -m pip install --upgrade pip