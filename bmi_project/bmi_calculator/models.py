"""
models.py

In Django, a "model" is a Python class that describes one SQL database table.

This app does NOT use Django models. Since Module 3 the BMI calculations are
saved in a Firebase Firestore cloud database (a NoSQL document database), which
is handled by firestore_service.py instead of Django's ORM. Each saved
calculation is a Firestore document with these fields:
    height_cm, weight_kg, bmi, category, note, created_at

The default SQLite database in settings.py is only used by Django's built-in
features (admin site, sessions), not for BMI data.
"""

from django.db import models

# Create your models here.
