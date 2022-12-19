import os

from django import setup

# Set the environment variable.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sail.settings")
# Setup django.
setup()
