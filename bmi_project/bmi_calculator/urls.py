"""
urls.py (app-level)

Maps URL paths to the view functions in views.py for the bmi_calculator app.
"""

from django.urls import path
from . import views

# 'name=' lets templates refer to these URLs by name instead of hard-coding
# paths, using the {% url %} template tag.
urlpatterns = [
    path("", views.home, name="home"),
    path("result/", views.result, name="result"),
    path("tips/", views.tips, name="tips"),
]
