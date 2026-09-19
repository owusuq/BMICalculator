"""
models.py

In Django, a "model" is a Python class that describes one database table:
each class attribute becomes a column, and each saved object becomes a row.
Django's ORM (object-relational mapper) turns these classes into SQL for us.

This BMI Calculator does NOT store anything in a database. Every BMI value is
calculated on the fly from the form input and then thrown away, so no models
are needed and this file is intentionally empty.

(The project still has a default SQLite database configured in settings.py --
Django sets that up automatically for its built-in features such as the admin
site and sessions -- but this app does not save any of its own data in it.)

The module requirement for this project is met by the "third dynamically
generated page" option (the tips page), not by the database option.

Future idea: add a model such as
    class BMIRecord(models.Model):
        height_cm = models.FloatField()
        weight_kg = models.FloatField()
        bmi = models.FloatField()
        created_at = models.DateTimeField(auto_now_add=True)
so that past calculations could be saved and shown as a history page.
"""

from django.db import models

# Create your models here.
